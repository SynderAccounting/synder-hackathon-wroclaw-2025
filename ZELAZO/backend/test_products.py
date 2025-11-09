"""Quick script to list products in database"""
import asyncio
from app.core.database import get_db
from app.repositories.products_repository import ProductsRepository


async def main():
    async for db in get_db():
        repo = ProductsRepository(db)
        products = await repo.get_all()
        print(f"\nFound {len(products)} products:")
        for p in products:
            print(f"  {p.id} - {p.name} (Category: {p.category}, Price: {p.price})")
        break

if __name__ == "__main__":
    asyncio.run(main())
