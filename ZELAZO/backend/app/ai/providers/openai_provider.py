"""OpenAI provider implementation using LangChain"""

from typing import Dict, Any
import json

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, SecretStr

from .base import AIProvider


class DashboardInsights(BaseModel):
    """Structured output for dashboard insights"""

    insights: list[str] = Field(
        description="List of 3-5 key insights from the dashboard data"
    )
    recommendations: list[str] = Field(
        description="List of 3-5 strategic recommendations based on the data"
    )
    summary: str = Field(
        description="Overall summary of the current sales situation (2-3 sentences)"
    )


class OpenAIProvider(AIProvider):
    """OpenAI implementation of AI provider using LangChain"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialise the OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.llm = ChatOpenAI(
            api_key=SecretStr(api_key),
            model=model,
            temperature=0.3  # Lower temperature for more consistent insights
        )

    async def generate_dashboard_insights(
        self,
        dashboard_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights and analysis for dashboard data using OpenAI.

        Args:
            dashboard_data: Dashboard statistics including income, orders, platforms

        Returns:
            Dictionary containing insights, recommendations, and summary
        """
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=DashboardInsights)

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert sales analyst for an e-commerce business
that sells products across multiple marketplaces (Amazon, Allegro, Temu).
Analyze the provided dashboard data and generate actionable insights and recommendations.
Focus on trends, anomalies, opportunities, and potential risks. Use British English.

{format_instructions}"""),
            ("user", """Analyse this sales dashboard data:

{dashboard_data}

Provide insights, recommendations, and a summary of the current sales situation.""")
        ])

        # Format the dashboard data nicely
        formatted_data = json.dumps(dashboard_data, indent=2)

        # Create the chain
        chain = prompt | self.llm | parser

        # Execute the chain
        result = await chain.ainvoke({
            "dashboard_data": formatted_data,
            "format_instructions": parser.get_format_instructions()
        })

        # Convert to dict
        return {
            "insights": result.insights,
            "recommendations": result.recommendations,
            "summary": result.summary
        }

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
        # Placeholder for future implementation
        # This will be implemented when product listing helper is needed
        return {
            "message": "Product listing analysis coming soon",
            "marketplace": marketplace,
            "product": product_data.get("name", "Unknown")
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
            Dictionary containing market overview, competition, target audience, marketplaces, and tips
        """
        # Define the structured output model
        class MarketOverview(BaseModel):
            demand: str = Field(description="Demand level: Low, Medium, or High")
            average_price: str = Field(description="Average price range in local currency")
            trend: str = Field(description="Market trend: Growing, Stable, or Declining")
            marketplaces: list[str] = Field(description="List of suitable marketplace names")

        class Competition(BaseModel):
            level: str = Field(description="Competition level: Low, Medium, or High")
            popular_brands: list[str] = Field(description="List of 2-4 popular competing brands")

        class TargetAudience(BaseModel):
            age: str = Field(description="Target age range (e.g., 18-35)")
            gender: str = Field(description="Target gender or gender preference")
            interests: list[str] = Field(description="List of 3-5 target audience interests")

        class MarketplaceRecommendation(BaseModel):
            name: str = Field(description="Marketplace name")
            description: str = Field(description="Brief description of why this marketplace is suitable")
            icon: str = Field(description="Icon identifier: flag.fill for national, globe for international, iphone for mobile-first")

        class OnboardingAnalysis(BaseModel):
            market_overview: MarketOverview
            competition: Competition
            target_audience: TargetAudience
            marketplaces: list[MarketplaceRecommendation] = Field(description="List of 3-5 recommended marketplaces")
            tips: list[str] = Field(description="List of 3-5 practical, actionable tips for starting to sell")

        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=OnboardingAnalysis)

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert e-commerce consultant specialising in helping new sellers enter online marketplaces.
Your role is to analyse product opportunities and provide data-driven, actionable recommendations.

Focus on:
- Real market data and trends for the specific country
- Practical, beginner-friendly marketplace recommendations
- Realistic pricing based on local market conditions
- Concrete, actionable tips that a new seller can implement immediately

Be specific to the country's e-commerce landscape and use local currency when mentioning prices.

{format_instructions}"""),
            ("user", """Analyse this product for selling in {country}:

Product: {product_name}
Description: {product_description}

Provide a comprehensive market analysis including:
1. Market overview (demand, pricing, trends, suitable marketplaces)
2. Competition analysis (level and key competitors)
3. Target audience profile
4. Specific marketplace recommendations with reasons
5. Practical tips for getting started

Be specific to {country}'s e-commerce market and culture.""")
        ])

        # Create the chain
        chain = prompt | self.llm | parser

        # Execute the chain
        result = await chain.ainvoke({
            "country": country,
            "product_name": product_name,
            "product_description": product_description,
            "format_instructions": parser.get_format_instructions()
        })

        # Convert to dict with proper structure
        return {
            "market_overview": {
                "demand": result.market_overview.demand,
                "average_price": result.market_overview.average_price,
                "trend": result.market_overview.trend,
                "marketplaces": result.market_overview.marketplaces
            },
            "competition": {
                "level": result.competition.level,
                "popular_brands": result.competition.popular_brands
            },
            "target_audience": {
                "age": result.target_audience.age,
                "gender": result.target_audience.gender,
                "interests": result.target_audience.interests
            },
            "marketplaces": [
                {
                    "name": mp.name,
                    "description": mp.description,
                    "icon": mp.icon
                }
                for mp in result.marketplaces
            ],
            "tips": result.tips
        }

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
            Dictionary with product_id, product_name, confidence, and reason
        """
        # If no candidates, return no match
        if not candidate_products:
            return {
                "product_id": None,
                "product_name": None,
                "confidence": 0.0,
                "reason": "No products in database to match against"
            }

        # Define structured output model
        class ProductMatch(BaseModel):
            product_id: str | None = Field(description="UUID of the best matching product, or null if no good match")
            product_name: str | None = Field(description="Name of the matched product, or null")
            confidence: float = Field(description="Confidence score 0.0-1.0. Use 0.8+ for strong matches, 0.5-0.79 for uncertain, <0.5 for poor matches", ge=0.0, le=1.0)
            reason: str = Field(description="Brief explanation of why this product was matched or why no match was found")

        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=ProductMatch)

        # Format candidate products for the prompt
        candidates_text = "\n".join([
            f"- ID: {p['id']}, Name: {p['name']}, Category: {p.get('category', 'N/A')}, "
            f"Price: {p.get('price', 'N/A')}, SKU: {p.get('sku', 'N/A')}, "
            f"Description: {(p.get('description') or 'N/A')[:100]}..."
            for p in candidate_products
        ])

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert product matching system for e-commerce platforms.
                Your task is to match external marketplace listings to internal product catalogue entries.

                MATCHING STRATEGY:
                - Product names are THE MOST IMPORTANT factor - even slight variations (case, punctuation, extra words) should match
                - If names are very similar (>70% match), consider it a strong candidate
                - Ignore minor differences: spaces, hyphens, capitalization, "premium", "pro", version numbers
                - Examples of matches: "iPhone 13" = "Iphone 13", "Wool socks" = "wool socks premium", "YouPhone 20" = "Pear YouPhone 20"

                Matching criteria (in order of importance):
                1. **Product name similarity** (MOST IMPORTANT - be generous with partial matches)
                   - Exact match or very close = 0.9-1.0
                   - Core product name matches with extras = 0.8-0.9
                   - Similar product with variations = 0.7-0.8
                2. Category match (helpful but not required)
                3. Price similarity (allow ±30% variance - prices vary across platforms)
                4. Description keywords (supportive evidence)

                Confidence scoring:
                - 1.0: Exact name match (ignoring case/punctuation)
                - 0.9-0.99: Very close name match (e.g., "Premium Socks" vs "Socks")
                - 0.8-0.89: Strong name similarity with same core product (e.g., "iPhone 13 Pro" vs "iPhone 13")
                - 0.7-0.79: Good name similarity, same type of product
                - 0.6-0.69: Moderate similarity, likely the same product family
                - Below 0.6: Different products or too uncertain

                CRITICAL RULES:
                1. You MUST ONLY use product IDs from the "Available products" list provided below
                2. NEVER generate, invent, or make up product IDs
                3. Copy the EXACT UUID string that appears after "ID: " in the product list
                4. If confidence < 0.6, return null for product_id
                5. Be GENEROUS with name matching - minor variations should still match
                6. Price differences are common across platforms - don't penalize heavily for price variance

                {format_instructions}"""),
                            ("user", """External listing to match:
                Name: {external_name}
                Description: {external_description}
                Price: {external_price}
                Marketplace: {marketplace}

                Available products in database:
                {candidates}

                TASK: Find the product with the most similar NAME from the list above. Be generous with name matching -
                if the core product name is the same (ignoring extras like "premium", "pro", version numbers),
                consider it a match. Copy the exact ID from the list. Only return null if truly no similar product exists.""")
        ])

        # Create the chain
        chain = prompt | self.llm | parser

        # Execute
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Calling OpenAI with external_name='{external_listing.get('name')}', candidates count={len(candidate_products)}")

        result = await chain.ainvoke({
            "external_name": external_listing.get("name", ""),
            "external_description": external_listing.get("description", "N/A"),
            "external_price": external_listing.get("price", "N/A"),
            "marketplace": external_listing.get("marketplace", "unknown"),
            "candidates": candidates_text,
            "format_instructions": parser.get_format_instructions()
        })

        logger.info(f"OpenAI returned: product_id={getattr(result, 'product_id', None)}, confidence={getattr(result, 'confidence', None)}")

        # CRITICAL VALIDATION: Verify the AI didn't hallucinate a product_id
        # Check if the returned product_id exists in our candidate list
        try:
            validated_product_id = None
            validated_product_name = getattr(result, 'product_name', None)
            validated_confidence = getattr(result, 'confidence', 0.0)
            validated_reason = getattr(result, 'reason', "No reason provided")

            result_product_id = getattr(result, 'product_id', None)

            if result_product_id:
                # Get list of valid IDs from candidates
                valid_ids = [p['id'] for p in candidate_products]
                if result_product_id in valid_ids:
                    validated_product_id = result_product_id
                else:
                    # AI hallucinated an ID that doesn't exist - reject it
                    logger.warning(f"AI hallucinated invalid product_id: {result_product_id}. Valid IDs: {valid_ids}")
                    validated_product_id = None
                    validated_product_name = None
                    validated_confidence = 0.0
                    validated_reason = f"AI error: suggested non-existent product. Original reason: {validated_reason}"

            return {
                "product_id": validated_product_id,
                "product_name": validated_product_name,
                "confidence": validated_confidence,
                "reason": validated_reason
            }
        except Exception as e:
            logger.error(f"Error in validation: {e}", exc_info=True)
            return {
                "product_id": None,
                "product_name": None,
                "confidence": 0.0,
                "reason": f"Validation error: {str(e)}"
            }
