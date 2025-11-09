"""Dashboard API controller"""

from fastapi import APIRouter, status
from app.api.schemas import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/v1", tags=["dashboard"])

# Initialise service instance
dashboard_service = DashboardService()


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard summary",
    description="Returns comprehensive dashboard data including health check, orders, income, and platform-specific statistics"
)
async def get_dashboard() -> DashboardResponse:
    """
    Get dashboard summary with all key metrics.

    Returns:
        DashboardResponse: Complete dashboard data including:
            - Health check status and message
            - Total orders this month
            - Total income this month
            - Platform-specific details (Amazon, Allegro, Temu)

    Example response:
        ```json
        {
            "health_check": {
                "status": "warning",
                "message": "Warning: decreased amount of sold goods"
            },
            "orders_amount_this_month": 1250,
            "income_this_month": 45780.50,
            "platforms": [
                {
                    "platform": "amazon",
                    "income_this_month": 25000.00,
                    "orders_this_month": 650,
                    "income_difference": -2500.00
                }
            ]
        }
        ```
    """
    return dashboard_service.get_dashboard_data()
