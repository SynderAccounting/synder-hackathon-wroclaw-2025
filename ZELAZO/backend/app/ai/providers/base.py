"""Base AI provider interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    async def generate_dashboard_insights(
        self,
        dashboard_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights and analysis for dashboard data.

        Args:
            dashboard_data: Dashboard statistics including income, orders, platforms

        Returns:
            Dictionary containing:
                - insights: List of key insights
                - recommendations: List of strategic recommendations
                - summary: Overall summary text
        """
        pass

    @abstractmethod
    async def analyze_product_listing(
        self,
        product_data: Dict[str, Any],
        marketplace: str
    ) -> Dict[str, Any]:
        """
        Analyze product data and provide listing recommendations.

        Args:
            product_data: Product information (name, category, price, etc.)
            marketplace: Target marketplace (amazon, allegro, temu)

        Returns:
            Dictionary containing listing recommendations
        """
        pass

    @abstractmethod
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
            Dictionary containing:
                - market_overview: Market demand, pricing, trend, marketplaces
                - competition: Competition level and popular brands
                - target_audience: Age, gender, interests
                - marketplaces: List of recommended marketplaces with descriptions
                - tips: Practical tips for starting to sell
        """
        pass

    @abstractmethod
    async def match_external_product(
        self,
        external_listing: Dict[str, Any],
        candidate_products: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Match an external listing to internal products using AI.

        Args:
            external_listing: External product data (name, description, price, etc.)
            candidate_products: List of potential matching products from database

        Returns:
            Dictionary containing:
                - product_id: UUID of matched product (or None)
                - product_name: Name of matched product (or None)
                - confidence: Match confidence score 0.0-1.0
                - reason: Explanation for the match or no-match
        """
        pass
