"""
Product matching service for external listings.
Implements 3-tier strategy: SKU match -> AI match -> No match
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from app.repositories.products_repository import ProductsRepository
from app.ai.ai_service import AIService


class ProductMatchingService:
    """Service for matching external listings to internal products."""

    def __init__(self, repository: ProductsRepository, ai_service: AIService):
        """
        Initialise the product matching service.

        Args:
            repository: ProductsRepository for database operations
            ai_service: AIService for AI-powered matching
        """
        self.repository = repository
        self.ai_service = ai_service

    async def match_external_listing(
        self,
        external_listing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match an external listing to an internal product using 3-tier strategy.

        Tier 1: SKU exact match (if external listing has SKU)
        Tier 2: AI-powered fuzzy matching
        Tier 3: No match found

        Args:
            external_listing: Dict containing name, description, sku (optional), price, etc.

        Returns:
            Dictionary with:
                - product_id: UUID or None
                - product_name: str or None
                - confidence: float 0.0-1.0
                - reason: str explanation
                - match_status: "exact" | "suggested" | "none"
        """
        logging.info("Starting product matching for external listing")
        # Tier 1: Try SKU/ID exact match first
        sku = external_listing.get("sku")
        if sku:
            product = await self.repository.get_by_sku_or_id(sku)
            logging.info(f"SKU match attempt for SKU '{sku}': {'Found' if product else 'Not found'}")
            if product:
                return {
                    "product_id": product.id,
                    "product_name": product.name,
                    "confidence": 1.0,
                    "reason": "Exact match (SKU or ID)",
                    "match_status": "exact"
                }

        # Tier 2: AI-powered matching
        if self.ai_service.is_enabled():
            logging.info("AI service is enabled, starting AI matching")
            # Get all products as candidates
            all_products = await self.repository.get_all()
            logging.info(f"Found {len(all_products)} products in database for AI matching")

            if all_products:
                # Convert to dict format for AI
                candidate_dicts = [
                    {
                        "id": str(product.id),
                        "name": product.name,
                        "category": product.category,
                        "price": float(product.price),
                        "sku": product.sku,
                        "description": product.description
                    }
                    for product in all_products
                ]

                logging.info(f"External listing for AI matching: name='{external_listing.get('name')}', price={external_listing.get('price')}")
                logging.info(f"Sample candidates: {candidate_dicts[:2]}")  # Log first 2 candidates

                # Use AI to find best match
                ai_match = await self.ai_service.match_external_product(
                    external_listing,
                    candidate_dicts
                )

                logging.info(f"AI match result: product_id={ai_match.get('product_id')}, confidence={ai_match.get('confidence')}, reason={ai_match.get('reason')}")

                # If AI found a confident match (>= 0.6)
                if ai_match.get("product_id") and ai_match.get("confidence", 0) >= 0.6:
                    logging.info(f"AI match accepted (confidence >= 0.6): {ai_match['product_name']}")
                    return {
                        "product_id": UUID(ai_match["product_id"]),
                        "product_name": ai_match["product_name"],
                        "confidence": ai_match["confidence"],
                        "reason": ai_match["reason"],
                        "match_status": "suggested" if ai_match["confidence"] < 0.8 else "exact"
                    }
                else:
                    logging.warning(f"AI match rejected (confidence < 0.6 or None): confidence={ai_match.get('confidence')}")
        else:
            logging.warning("AI service is NOT enabled")

        # Tier 3: No match found
        return {
            "product_id": None,
            "product_name": None,
            "confidence": 0.0,
            "reason": "No matching product found in database" if not self.ai_service.is_enabled()
                     else "No confident match found (AI threshold not met)",
            "match_status": "none"
        }
