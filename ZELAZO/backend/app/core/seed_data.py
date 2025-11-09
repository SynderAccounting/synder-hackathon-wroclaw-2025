"""
Database seeding utility for initial product data.
Seeds the database with sample products if the products table is empty.
"""
import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product

logger = logging.getLogger(__name__)


SAMPLE_PRODUCTS = [
    {
        "name": "Pear YouPhone 20",
        "category": "Smartphone",
        "price": Decimal("1555.99"),
        "sku": "PHONE-PEAR-20",
        "description": "Flagship 2025 smartphone with superior camera and 5G connectivity"
    },
    {
        "name": "SamSing Galaxy S24",
        "category": "Smartphone",
        "price": Decimal("1299.99"),
        "sku": "PHONE-SAM-S24",
        "description": "Premium Android smartphone with stunning AMOLED display"
    },
    {
        "name": "Wireless Earbuds Pro",
        "category": "Audio",
        "price": Decimal("199.99"),
        "sku": "AUDIO-BUDS-PRO",
        "description": "High-quality wireless earbuds with active noise cancellation"
    },
    {
        "name": "Smart Watch Ultra",
        "category": "Wearables",
        "price": Decimal("449.99"),
        "sku": "WATCH-ULTRA-01",
        "description": "Advanced fitness tracking smartwatch with GPS and heart rate monitor"
    },
    {
        "name": "Laptop ProBook 15",
        "category": "Computers",
        "price": Decimal("2499.99"),
        "sku": "LAPTOP-PRO-15",
        "description": "Professional laptop with Intel i9 processor and 32GB RAM"
    },
    {
        "name": "Mechanical Keyboard RGB",
        "category": "Accessories",
        "price": Decimal("159.99"),
        "sku": "KB-MECH-RGB",
        "description": "Gaming mechanical keyboard with customizable RGB lighting"
    },
    {
        "name": "4K Webcam HD",
        "category": "Accessories",
        "price": Decimal("89.99"),
        "sku": "CAM-4K-HD",
        "description": "Professional 4K webcam for streaming and video calls"
    },
    {
        "name": "Portable SSD 1TB",
        "category": "Storage",
        "price": Decimal("129.99"),
        "sku": "SSD-PORT-1TB",
        "description": "Fast portable SSD with 1TB storage and USB-C connectivity"
    },
    {
        "name": "Wireless Mouse Elite",
        "category": "Accessories",
        "price": Decimal("49.99"),
        "sku": "MOUSE-ELITE-WL",
        "description": "Ergonomic wireless mouse with precision tracking"
    },
    {
        "name": "USB-C Hub 7-in-1",
        "category": "Accessories",
        "price": Decimal("39.99"),
        "sku": "HUB-USBC-7",
        "description": "Multi-port USB-C hub with HDMI, USB 3.0, and SD card reader"
    },
    {
        "name": "Bluetooth Speaker Portable",
        "category": "Audio",
        "price": Decimal("79.99"),
        "sku": "SPEAKER-BT-PORT",
        "description": "Waterproof portable Bluetooth speaker with 20-hour battery life"
    },
    {
        "name": "Phone Case Premium Leather",
        "category": "Accessories",
        "price": Decimal("34.99"),
        "sku": "CASE-LEATHER-01",
        "description": "Premium leather phone case with card holder"
    },
    {
        "name": "Screen Protector Tempered Glass",
        "category": "Accessories",
        "price": Decimal("14.99"),
        "sku": "SCREEN-GLASS-01",
        "description": "9H tempered glass screen protector with easy installation"
    },
    {
        "name": "Power Bank 20000mAh",
        "category": "Accessories",
        "price": Decimal("59.99"),
        "sku": "POWER-20K-01",
        "description": "High-capacity power bank with fast charging and dual USB ports"
    },
    {
        "name": "Tablet Pro 12.9",
        "category": "Tablets",
        "price": Decimal("1099.99"),
        "sku": "TABLET-PRO-12",
        "description": "Professional tablet with stylus support and laptop-grade performance"
    },
    {
        "name": "Gaming Headset 7.1",
        "category": "Audio",
        "price": Decimal("129.99"),
        "sku": "HEADSET-GAME-71",
        "description": "Immersive 7.1 surround sound gaming headset with noise-canceling mic"
    },
    {
        "name": "Wireless Charger 15W",
        "category": "Accessories",
        "price": Decimal("29.99"),
        "sku": "CHARGER-WL-15W",
        "description": "Fast wireless charging pad compatible with all Qi-enabled devices"
    },
    {
        "name": "Fitness Tracker Band",
        "category": "Wearables",
        "price": Decimal("89.99"),
        "sku": "FITNESS-BAND-01",
        "description": "Affordable fitness tracker with sleep monitoring and step counter"
    },
    {
        "name": "External Hard Drive 2TB",
        "category": "Storage",
        "price": Decimal("79.99"),
        "sku": "HDD-EXT-2TB",
        "description": "Reliable 2TB external hard drive for backup and storage"
    },
    {
        "name": "Smart Home Hub",
        "category": "Smart Home",
        "price": Decimal("149.99"),
        "sku": "SMARTHOME-HUB-01",
        "description": "Central smart home hub compatible with Alexa and Google Home"
    }
]


async def seed_products(session: AsyncSession) -> None:
    """
    Seed the products table with sample data if it's empty.

    Args:
        session: AsyncSession database session
    """
    try:
        # Check if products table is empty
        result = await session.execute(select(Product))
        existing_products = result.scalars().all()

        if len(existing_products) > 0:
            logger.info(f"Products table already contains {len(existing_products)} products. Skipping seed.")
            return

        logger.info("Products table is empty. Seeding with sample data...")

        # Create sample products
        products_created = 0
        for product_data in SAMPLE_PRODUCTS:
            product = Product(**product_data)
            session.add(product)
            products_created += 1

        await session.commit()
        logger.info(f"✓ Successfully seeded {products_created} products into the database")

    except Exception as e:
        logger.error(f"Error seeding products: {e}", exc_info=True)
        await session.rollback()
        raise


async def seed_database(session: AsyncSession) -> None:
    """
    Main seeding function that seeds all tables.

    Args:
        session: AsyncSession database session
    """
    logger.info("Starting database seeding...")
    await seed_products(session)
    logger.info("Database seeding completed")
