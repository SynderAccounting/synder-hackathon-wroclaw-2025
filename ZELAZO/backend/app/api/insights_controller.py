"""Insights API controller for AI-powered analytics"""

from fastapi import APIRouter, Depends, status

from app.api.schemas import InsightsResponse
from app.services.dashboard_service import DashboardService
from app.ai.ai_service import AIService, create_ai_service
from app.core.config import settings

router = APIRouter(prefix="/v1", tags=["insights"])


# Create singleton AI service instance
ai_service_instance = create_ai_service(settings.OPENAI_API_KEY)


def get_ai_service() -> AIService:
    """
    Dependency function to get AI service instance.

    Returns:
        AIService: Singleton AI service instance
    """
    return ai_service_instance


def get_dashboard_service() -> DashboardService:
    """
    Dependency function to get dashboard service instance.

    Returns:
        DashboardService: Dashboard service for retrieving data
    """
    return DashboardService()


@router.get(
    "/insights",
    response_model=InsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI-powered dashboard insights",
    description="""Generate AI-powered insights and recommendations based on current dashboard data.

    This endpoint analyses your sales data across all platforms and provides:
    - Key insights about performance and trends
    - Strategic recommendations for improving sales
    - Overall summary of the current business situation

    **Note:** Requires OPENAI_API_KEY to be configured in environment variables.
    If not configured, will return a message indicating AI is not available.
    """
)
async def get_insights(
    ai_service: AIService = Depends(get_ai_service),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
) -> InsightsResponse:
    """
    Get AI-powered insights for the dashboard.

    This endpoint retrieves current dashboard data and uses AI to generate
    actionable insights, strategic recommendations, and an overall summary.

    Returns:
        InsightsResponse: AI-generated insights including:
            - insights: List of 3-5 key observations
            - recommendations: List of 3-5 strategic actions
            - summary: Overall assessment (2-3 sentences)
            - ai_enabled: Whether AI service is functioning

    Example response (when AI is enabled):
        ```json
        {
            "insights": [
                "Amazon generates the highest revenue with £25,000 this month",
                "Temu shows strong growth with 5% increase month-over-month",
                "Allegro orders decreased by 10%, indicating potential challenges"
            ],
            "recommendations": [
                "Investigate the decline in Allegro sales",
                "Expand product listings on Temu to capitalize on growth",
                "Consider promotional campaigns on underperforming platforms"
            ],
            "summary": "Overall sales are healthy with £48,500 in revenue...",
            "ai_enabled": true
        }
        ```

    Example response (when AI is not configured):
        ```json
        {
            "insights": ["AI insights are not available - API key not configured"],
            "recommendations": ["Configure OpenAI API key in .env file"],
            "summary": "AI service is not configured. Add OPENAI_API_KEY...",
            "ai_enabled": false
        }
        ```
    """
    # Get current dashboard data
    dashboard_data = dashboard_service.get_dashboard_data()

    # Convert to dict for AI processing
    dashboard_dict = dashboard_data.model_dump()

    # Generate insights using AI service
    insights = await ai_service.generate_dashboard_insights(dashboard_dict)

    return InsightsResponse(**insights)
