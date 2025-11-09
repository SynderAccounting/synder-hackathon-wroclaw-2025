from db.connection import get_db_connection
from db.orders import insert_order
from models.order import Order
from order_generator.generator import OrderGenerator

import sys
from pathlib import Path

# Add necessary paths for imports
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path / "mock_api"))
sys.path.insert(0, str(root_path / "db_client"))



def create_order_from_data(order_data, service: str) -> Order:
    """Create an Order instance from OrderData with specified service.

    Args:
        order_data: Generated OrderData instance.
        service: Service name ("Amazon", "Etsy", or "Shopify").

    Returns:
        Order instance ready to insert into database.
    """
    return Order(
        service=service,
        order_id=order_data.order_id,
        created_at=order_data.created_at,
        updated_at=order_data.updated_at,
        currency=order_data.currency,
        financial_status=order_data.financial_status,
        subtotal=order_data.subtotal,
        discount=order_data.discount,
        total_tax=order_data.total_tax,
        final_price=order_data.final_price,
        billing_address=order_data.billing_address,
        shipping_address=order_data.shipping_address,
        items=order_data.items,
        fulfillment=order_data.fulfillment,
        customer=order_data.customer,
    )


def populate_orders(service: str, count: int, merchant_id: int, generator: OrderGenerator) -> tuple[int, int]:
    """Generate and insert multiple orders for a service.

    Args:
        service: Service name ("Amazon", "Etsy", or "Shopify").
        count: Number of orders to generate.
        merchant_id: ID of the merchant who owns these orders.
        generator: OrderGenerator instance.

    Returns:
        Tuple of (orders inserted, total items inserted).
    """
    print(f"Generating {count} {service} orders...")
    inserted_orders = 0
    total_items = 0

    with get_db_connection() as conn:
        for i in range(count):
            order_data = generator.generate_order_data()
            order = create_order_from_data(order_data, service)

            try:
                insert_order(conn, order, merchant_id)
                conn.commit()
                inserted_orders += 1
                # Count items in this order
                items_count = sum(item.quantity for item in order.items)
                total_items += items_count

                # Print progress every 50 orders
                if (i + 1) % 50 == 0:
                    print(f"  Inserted {i + 1}/{count} orders ({total_items} items so far)...")
            except Exception as e:
                conn.rollback()
                print(f"  Error inserting order {order.order_id}: {e}")

    print(f"Successfully inserted {inserted_orders}/{count} {service} orders ({total_items} total items)\n")
    return inserted_orders, total_items


def populate_orders_target_items(service: str, target_items: int, merchant_id: int, generator: OrderGenerator) -> tuple[int, int]:
    """Generate and insert orders until reaching target item count.

    Args:
        service: Service name ("Amazon", "Etsy", or "Shopify").
        target_items: Target number of items to sell.
        merchant_id: ID of the merchant who owns these orders.
        generator: OrderGenerator instance.

    Returns:
        Tuple of (orders inserted, total items inserted).
    """
    print(f"Generating {service} orders to reach ~{target_items} items...")
    inserted_orders = 0
    total_items = 0

    with get_db_connection() as conn:
        while total_items < target_items:
            order_data = generator.generate_order_data()
            order = create_order_from_data(order_data, service)

            try:
                insert_order(conn, order, merchant_id)
                conn.commit()
                inserted_orders += 1
                # Count items in this order
                items_count = sum(item.quantity for item in order.items)
                total_items += items_count

                # Print progress every 20 orders
                if inserted_orders % 20 == 0:
                    print(f"  Inserted {inserted_orders} orders ({total_items} items so far)...")
            except Exception as e:
                conn.rollback()
                print(f"  Error inserting order {order.order_id}: {e}")

    print(f"Successfully inserted {inserted_orders} {service} orders ({total_items} total items)\n")
    return inserted_orders, total_items


def main():
    """Main function to populate database with mock orders."""
    # Configuration - Each merchant gets orders from all services
    # Format: (Amazon, Etsy, Shopify)
    MERCHANT_1_ORDERS = (200, 150, 100)  # Total: 450 orders
    MERCHANT_2_ORDERS = (150, 200, 120)  # Total: 470 orders
    MERCHANT_3_ORDERS = (180, 160, 200)  # Total: 540 orders

    print("=" * 60)
    print("Mock Order Database Population Script")
    print("=" * 60)
    print()

    # Initialize order generator
    generator = OrderGenerator()

    # Populate orders for each merchant across all services
    total_orders = 0
    total_items = 0

    # Merchant 1
    print("MERCHANT 1 (mixed services)")
    print("-" * 60)
    orders, items = populate_orders("Amazon", MERCHANT_1_ORDERS[0], 1, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Etsy", MERCHANT_1_ORDERS[1], 1, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Shopify", MERCHANT_1_ORDERS[2], 1, generator)
    total_orders += orders
    total_items += items
    print()

    # Merchant 2
    print("MERCHANT 2 (mixed services)")
    print("-" * 60)
    orders, items = populate_orders("Amazon", MERCHANT_2_ORDERS[0], 2, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Etsy", MERCHANT_2_ORDERS[1], 2, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Shopify", MERCHANT_2_ORDERS[2], 2, generator)
    total_orders += orders
    total_items += items
    print()

    # Merchant 3
    print("MERCHANT 3 (mixed services)")
    print("-" * 60)
    orders, items = populate_orders("Amazon", MERCHANT_3_ORDERS[0], 3, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Etsy", MERCHANT_3_ORDERS[1], 3, generator)
    total_orders += orders
    total_items += items

    orders, items = populate_orders("Shopify", MERCHANT_3_ORDERS[2], 3, generator)
    total_orders += orders
    total_items += items

    # Summary
    print("=" * 60)
    print(f"Total orders inserted: {total_orders}")
    print(f"Total items sold: {total_items}")
    print(f"Merchant 1: {sum(MERCHANT_1_ORDERS)} orders")
    print(f"Merchant 2: {sum(MERCHANT_2_ORDERS)} orders")
    print(f"Merchant 3: {sum(MERCHANT_3_ORDERS)} orders")
    print("=" * 60)


if __name__ == "__main__":
    main()
