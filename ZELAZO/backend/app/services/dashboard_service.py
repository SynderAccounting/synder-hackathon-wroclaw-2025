"""
Dashboard service containing business logic for dashboard operations.
"""
from app.api.schemas import DashboardResponse, HealthCheck, HealthStatus, PlatformDetails


class DashboardService:
    """Service class for dashboard-related business logic."""

    def __init__(self):
        """Initialise the dashboard service."""
        pass

    def get_dashboard_data(self) -> DashboardResponse:
        """
        Retrieve dashboard data including health check, orders, income, and platform statistics.

        Returns:
            DashboardResponse: Complete dashboard data with health metrics and platform details
        """
        # Platform-specific data
        platforms_data = [
            PlatformDetails(
                platform="amazon",
                income_this_month=25000.00,
                orders_this_month=650,
                income_difference=-2500.00
            ),
            PlatformDetails(
                platform="allegro",
                income_this_month=15000.50,
                orders_this_month=450,
                income_difference=1200.50
            ),
            PlatformDetails(
                platform="temu",
                income_this_month=5780.00,
                orders_this_month=150,
                income_difference=780.00
            )
        ]

        # Calculate total income and orders
        total_income = sum(p.income_this_month for p in platforms_data)
        total_orders = sum(p.orders_this_month for p in platforms_data)
        total_difference = sum(p.income_difference for p in platforms_data)

        # Determine health status based on income difference
        if total_difference < -2000.00:
            health_status = HealthStatus.CRITICAL
            health_message = "Revenue significantly below last month"
        elif total_difference < 0:
            health_status = HealthStatus.WARNING
            health_message = "Revenue slightly below last month"
        else:
            health_status = HealthStatus.OK
            health_message = "All systems operational"

        health_check = HealthCheck(
            status=health_status,
            message=health_message
        )

        return DashboardResponse(
            health_check=health_check,
            orders_amount_this_month=total_orders,
            income_this_month=total_income,
            platforms=platforms_data
        )