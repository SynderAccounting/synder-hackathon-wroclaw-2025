import asyncio
from typing import List

import aiohttp

from configs.config import N8N_CONFIG
from schemas.shopify import ShopifySchema


async def fetch_products(session: aiohttp.ClientSession, url: str) -> List[ShopifySchema]:
    async with session.post(url) as response:
        response.raise_for_status()
        data = await response.json()
        return [ShopifySchema(**product) for product in data]


async def get_shopify_data_async() -> List[ShopifySchema]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_products(session, url) for url in N8N_CONFIG.url]
        results = await asyncio.gather(*tasks)
        return [product for sublist in results for product in sublist]


async def get_shopify_data() -> List[ShopifySchema]:
    return await get_shopify_data_async()
