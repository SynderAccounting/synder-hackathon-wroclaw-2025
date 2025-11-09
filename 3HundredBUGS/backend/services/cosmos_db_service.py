from typing import List, Any

import asyncpg
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from configs.config import AZURE_COSMOS_DB_CONFIG, POSTGRESQL_CONFIG
from schemas.cosmos import SupplierProductSchema


async def get_all_suppliers_from_container() -> List[SupplierProductSchema]:
    items = []
    async with CosmosClient(AZURE_COSMOS_DB_CONFIG.uri, AZURE_COSMOS_DB_CONFIG.key) as client:
        try:
            database = client.get_database_client(AZURE_COSMOS_DB_CONFIG.database_name)
            container = database.get_container_client(AZURE_COSMOS_DB_CONFIG.supplier_container_name)
            async for item in container.read_all_items():
                items.append(item)
        except CosmosHttpResponseError as e:
            raise e
    return items


async def query_orders_container(query: str) -> Any:
    conn = None
    try:
        conn = await asyncpg.connect(POSTGRESQL_CONFIG.jdbc_url)
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    except Exception as e:
        raise e
    finally:
        if conn:
            await conn.close()
