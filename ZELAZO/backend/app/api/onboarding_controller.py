"""Onboarding API controller for new seller market analysis"""

from fastapi import APIRouter, Depends, status

from app.api.schemas import OnboardingRequest, OnboardingResponse
from app.ai.ai_service import AIService, create_ai_service
from app.core.config import settings

router = APIRouter(prefix="/onboarding/v1", tags=["onboarding"])


# Create singleton AI service instance
ai_service_instance = create_ai_service(settings.OPENAI_API_KEY)


def get_ai_service() -> AIService:
    """
    Dependency function to get AI service instance.

    Returns:
        AIService: Singleton AI service instance
    """
    return ai_service_instance


@router.post(
    "/analyse",
    response_model=OnboardingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI-powered market analysis for new sellers",
    description="""Generate comprehensive market analysis and selling strategy recommendations for onboarding new sellers.

    This endpoint analyses the product and target market to provide:
    - Market overview (demand, pricing trends, suitable marketplaces)
    - Competition analysis (level and popular brands)
    - Target audience profile (demographics and interests)
    - Specific marketplace recommendations with reasoning
    - Practical tips for getting started

    **Note:** Requires OPENAI_API_KEY to be configured in environment variables.
    If not configured, will return a message indicating AI is not available.

    **Input:**
    - country: Target country for selling (e.g., "Poland", "UK", "USA")
    - product_name: Name of the product to sell
    - product_description: Detailed description of the product

    **Output:**
    Complete market analysis with actionable recommendations tailored to the specific country and product.
    """
)
async def analyze_market(
    request: OnboardingRequest,
    ai_service: AIService = Depends(get_ai_service)
) -> OnboardingResponse:
    """
    Analyse market opportunity for a new seller.

    This endpoint uses AI to generate comprehensive market analysis including:
    - Market demand, pricing, and trends specific to the target country
    - Competition landscape and key players
    - Target customer demographics and interests
    - Recommended marketplaces with specific reasons why each is suitable
    - Actionable tips for starting to sell successfully

    Args:
        request: OnboardingRequest containing country, product_name, and product_description
        ai_service: Injected AI service instance

    Returns:
        OnboardingResponse: Comprehensive market analysis and recommendations

    Example request:
        ```json
        {
            "country": "Poland",
            "product_name": "Handmade Wool Hoodie",
            "product_description": "High-quality streetwear hoodie made from organic wool, featuring unique embroidered designs."
        }
        ```

    Example response (when AI is enabled):
        ```json
        {
            "market_overview": {
                "demand": "High",
                "average_price": "120-180 zł",
                "trend": "Growing",
                "marketplaces": ["Allegro", "Zalando", "OLX", "Etsy"]
            },
            "competition": {
                "level": "Medium",
                "popular_brands": ["Local Heroes", "Reserved", "2005"]
            },
            "target_audience": {
                "age": "18-35",
                "gender": "Mostly male",
                "interests": ["Streetwear", "comfort", "unique design"]
            },
            "marketplaces": [
                {
                    "name": "Allegro",
                    "description": "easiest to start, high traffic",
                    "icon": "flag.fill"
                },
                ...
            ],
            "tips": [
                "Start with Allegro – lower entry barrier",
                "Use street-style photos for better engagement",
                ...
            ],
            "ai_enabled": true
        }
        ```
    """
    # Generate market analysis using AI service
    analysis = await ai_service.generate_onboarding_analysis(
        country=request.country,
        product_name=request.product_name,
        product_description=request.product_description
    )

    return OnboardingResponse(**analysis)
