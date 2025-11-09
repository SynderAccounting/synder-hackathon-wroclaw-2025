from fastapi import APIRouter

from configs.logger import LOGGER

health_router = APIRouter()


@health_router.get("")
async def health_endpoint():
    """Health check endpoint to verify if the service is running.
    """
    LOGGER.debug("Health check endpoint is running.")
    return {"status": "ok"}
