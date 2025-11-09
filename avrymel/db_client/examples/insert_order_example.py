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


def populate_orders(service: str, count: int, generator: OrderGenerator) -> int:
    """Generate and insert multiple orders for a service.

    Args:
        service: Service name ("Amazon", "Etsy", or "Shopify").
        count: Number of orders to generate.
        generator: OrderGenerator instance.

    Returns:
        Number of orders successfully inserted.
    """
    print(f"Generating {count} {service} orders...")
    inserted = 0

    with get_db_connection() as conn:
        for i in range(count):
            order_data = generator.generate_order_data()
            order = create_order_from_data(order_data, service)

            try:
                insert_order(conn, order)
                inserted += 1

                # Print progress every 50 orders
                if (i + 1) % 50 == 0:
                    print(f"  Inserted {i + 1}/{count} orders...")
            except Exception as e:
                print(f"  Error inserting order {order.order_id}: {e}")

    print(f"Successfully inserted {inserted}/{count} {service} orders\n")
    return inserted


def main():
    """Main function to populate database with mock orders."""
    # Configuration
    AMAZON_ORDERS = 100
    ETSY_ORDERS = 300
    SHOPIFY_ORDERS = 200

    print("=" * 60)
    print("Mock Order Database Population Script")
    print("=" * 60)
    print()

    # Initialize order generator
    generator = OrderGenerator()

    # Populate orders for each service
    total_inserted = 0
    total_inserted += populate_orders("Amazon", AMAZON_ORDERS, generator)
    total_inserted += populate_orders("Etsy", ETSY_ORDERS, generator)
    total_inserted += populate_orders("Shopify", SHOPIFY_ORDERS, generator)

    # Summary
    print("=" * 60)
    print(f"Total orders inserted: {total_inserted}")
    print("=" * 60)


if __name__ == "__main__":
    main()
