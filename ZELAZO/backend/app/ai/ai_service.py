"""Main AI service for coordinating AI operations"""

from typing import Dict, Any, Optional

from app.ai.providers.base import AIProvider
from app.ai.providers.openai_provider import OpenAIProvider


class AIService:
    """Service for AI-powered analytics and insights"""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialise the AI service.

        Args:
            provider: AI provider instance. If None, service will operate in degraded mode.
        """
        self.provider = provider
        self._is_enabled = provider is not None

    def is_enabled(self) -> bool:
        """Check if AI service is enabled (provider is configured)"""
        return self._is_enabled

    async def generate_dashboard_insights(
        self,
        dashboard_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights for dashboard data.

        Args:
            dashboard_data: Dashboard statistics

        Returns:
            Dictionary with insights, recommendations, and summary.
            If AI is disabled, returns fallback message.
        """
        if not self._is_enabled:
            return {
                "insights": ["AI insights are not available - API key not configured"],
                "recommendations": [
                    "Configure OpenAI API key in .env file to enable AI insights"
                ],
                "summary": "AI service is not configured. Add OPENAI_API_KEY to your environment variables to enable intelligent insights.",
                "ai_enabled": False
            }

        try:
            result = await self.provider.generate_dashboard_insights(dashboard_data)
            result["ai_enabled"] = True
            return result
        except Exception as e:
            # Fallback in case of AI provider errors
            return {
                "insights": [f"Error generating AI insights: {str(e)}"],
                "recommendations": ["Check AI provider configuration and API key"],
                "summary": "AI service encountered an error. Please check configuration.",
                "ai_enabled": False,
                "error": str(e)
            }

    async def analyze_product_listing(
        self,
        product_data: Dict[str, Any],
        marketplace: str
    ) -> Dict[str, Any]:
        """
        Analyze product for marketplace listing.

        Args:
            product_data: Product information
            marketplace: Target marketplace

        Returns:
            Dictionary with listing recommendations
        """
        if not self._is_enabled:
            return {
                "message": "AI product listing analysis not available - API key not configured",
                "ai_enabled": False
            }

        try:
            result = await self.provider.analyze_product_listing(product_data, marketplace)
            result["ai_enabled"] = True
            return result
        except Exception as e:
            return {
                "message": f"Error analyzing product: {str(e)}",
                "ai_enabled": False,
                "error": str(e)
            }

    async def generate_onboarding_analysis(
        self,
        country: str,
        product_name: str,
        product_description: str
    ) -> Dict[str, Any]:
        """
        Generate market analysis and selling strategy for onboarding.

        Args:
            country: Target country for selling
            product_name: Name of the product
            product_description: Description of the product

        Returns:
            Dictionary with market analysis and recommendations.
            If AI is disabled, returns fallback message.
        """
        if not self._is_enabled:
            return {
                "market_overview": {
                    "demand": "Unknown",
                    "average_price": "Not available",
                    "trend": "Unknown",
                    "marketplaces": []
                },
                "competition": {
                    "level": "Unknown",
                    "popular_brands": []
                },
                "target_audience": {
                    "age": "Not available",
                    "gender": "Not available",
                    "interests": []
                },
                "marketplaces": [],
                "tips": [
                    "AI onboarding analysis is not available - API key not configured",
                    "Configure OpenAI API key in .env file to enable market analysis",
                    "Research your local marketplaces manually for now"
                ],
                "ai_enabled": False
            }

        try:
            result = await self.provider.generate_onboarding_analysis(
                country, product_name, product_description
            )
            result["ai_enabled"] = True
            return result
        except Exception as e:
            return {
                "market_overview": {
                    "demand": "Error",
                    "average_price": "Error",
                    "trend": "Error",
                    "marketplaces": []
                },
                "competition": {
                    "level": "Error",
                    "popular_brands": []
                },
                "target_audience": {
                    "age": "Error",
                    "gender": "Error",
                    "interests": []
                },
                "marketplaces": [],
                "tips": [f"Error generating analysis: {str(e)}"],
                "ai_enabled": False,
                "error": str(e)
            }

    async def match_external_product(
        self,
        external_listing: Dict[str, Any],
        candidate_products: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Match external listing to internal products using AI.

        Args:
            external_listing: External product data
            candidate_products: List of potential matching products

        Returns:
            Dictionary with product_id, product_name, confidence, and reason
        """
        if not self._is_enabled:
            return {
                "product_id": None,
                "product_name": None,
                "confidence": 0.0,
                "reason": "AI matching not available - API key not configured"
            }

        try:
            result = await self.provider.match_external_product(
                external_listing, candidate_products
            )
            return result
        except Exception as e:
            return {
                "product_id": None,
                "product_name": None,
                "confidence": 0.0,
                "reason": f"Error during AI matching: {str(e)}"
            }


def create_ai_service(openai_api_key: Optional[str] = None) -> AIService:
    """
    Factory function to create AI service with appropriate provider.

    Args:
        openai_api_key: OpenAI API key. If None, service runs in degraded mode.

    Returns:
        AIService instance
    """
    if openai_api_key:
        provider = OpenAIProvider(api_key=openai_api_key)
        return AIService(provider=provider)
    else:
        # Return service without provider - will operate in degraded mode
        return AIService(provider=None)
