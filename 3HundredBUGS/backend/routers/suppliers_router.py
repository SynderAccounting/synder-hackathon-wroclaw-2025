from typing import List

from fastapi import APIRouter, HTTPException

from configs.logger import LOGGER
from schemas.cosmos import SupplierProductSchema
from services.cosmos_db_service import get_all_suppliers_from_container

supplier_router = APIRouter()


@supplier_router.get(
    "/all",
    summary="Get all suppliers information."
)
async def get_all_suppliers() -> List[SupplierProductSchema]:
    LOGGER.debug("Fetching all suppliers information")
    try:
        return await get_all_suppliers_from_container()
    except Exception as e:
        LOGGER.error("Error fetching suppliers information: {e}")
        raise HTTPException(status_code=404, detail="Suppliers information not found")
