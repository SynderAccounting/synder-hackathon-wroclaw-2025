"""Core orchestration for generating inventory recommendations."""
from __future__ import annotations

import logging
from typing import List, Optional, Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.anomaly_detection import TrendDetector
from app.ml.feature_engineering import FeatureEngineer
from app.ml.forecasting import DemandForecaster
from app.ml.models import Recommendation, RecommendationPriority, RecommendationType, StockMetrics, TrendSignal
from app.services.preference_learning_service import PreferenceLearningService
from models.catalog import Product

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Coordinates feature engineering, forecasting, and rule evaluation with preference learning."""

    def __init__(self, db: Session):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)
        self.forecaster = DemandForecaster(db, self.feature_engineer)
        self.trend_detector = TrendDetector(db, self.feature_engineer)
        self.preference_service = PreferenceLearningService(db)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations with preference learning to avoid dismissed suggestions."""
        logger.info("Starting recommendation generation...")

        # Get excluded recommendations based on user preferences
        excluded = self.preference_service.get_excluded_recommendations()
        logger.info(f"Excluding {len(excluded)} previously dismissed recommendations")

        # Get dismissal stats for insights
        stats = self.preference_service.get_dismissal_stats()
        logger.info(f"Preference stats: {stats}")

        # Detect trends and slow movers
        try:
            trending_signals = {signal.sku: signal for signal in self.trend_detector.detect_trending_products()}
            logger.info(f"Detected {len(trending_signals)} trending products")
        except Exception as e:
            logger.error(f"Error detecting trending products: {e}")
            trending_signals = {}

        try:
            slow_signals = {signal.sku: signal for signal in self.trend_detector.detect_slow_movers()}
            logger.info(f"Detected {len(slow_signals)} slow moving products")
        except Exception as e:
            logger.error(f"Error detecting slow movers: {e}")
            slow_signals = {}

        recommendations: List[Recommendation] = []
        products = list(self._iter_products())
        total_products = len(products)
        logger.info(f"Processing {total_products} products...")

        for idx, product in enumerate(products, 1):
            if idx % 10 == 0:
                logger.info(f"Processed {idx}/{total_products} products...")

            try:
                metrics = self.feature_engineer.calculate_stock_metrics(product.sku)
                if not metrics:
                    continue

                # Check for restock needs
                rec = self.check_restock_need(metrics)
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
                elif rec and self._is_excluded(rec, excluded):
                    # Try alternative approach
                    alt_rec = self._try_alternative(rec, metrics)
                    if alt_rec:
                        recommendations.append(alt_rec)

                # Check for trending products
                rec = self.check_trending(metrics, trending_signals.get(product.sku))
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
                elif rec and self._is_excluded(rec, excluded):
                    alt_rec = self._try_alternative(rec, metrics)
                    if alt_rec:
                        recommendations.append(alt_rec)

                # Check for slow movers
                rec = self.check_slow_mover(metrics, slow_signals.get(product.sku))
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
                elif rec and self._is_excluded(rec, excluded):
                    alt_rec = self._try_alternative(rec, metrics)
                    if alt_rec:
                        recommendations.append(alt_rec)

                # Check for seasonal patterns
                rec = self.check_seasonal_forecast(metrics)
                if rec:
                    recommendations.append(rec)
                
                # Check for optimization opportunities (products with good sales but could use more stock)
                rec = self.check_optimization_opportunity(metrics)
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
                
                # Check for new products with no sales history
                rec = self.check_new_product(metrics)
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
                
                # Check for general low stock situations
                rec = self.check_low_stock_alert(metrics)
                if rec and not self._is_excluded(rec, excluded):
                    recommendations.append(rec)
            except Exception as e:
                logger.error(f"Error processing product {product.sku}: {e}")
                continue

        # Sort by priority and confidence
        recommendations.sort(key=lambda rec: (self._priority_bucket(rec.priority), rec.confidence), reverse=True)
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    # ------------------------------------------------------------------
    # Rule evaluation helpers
    # ------------------------------------------------------------------
    def check_restock_need(self, metrics: StockMetrics) -> Optional[Recommendation]:
        """Enhanced restock check with improved confidence calculation."""
        forecast = self.forecaster.predict_demand(metrics.sku, horizon_days=14)
        avg_daily_sales = max(metrics.avg_daily_sales_30d, forecast.daily_demand)
        
        # If no sales history, use a conservative estimate for products with stock
        if not avg_daily_sales and metrics.current_stock > 0:
            # Assume 1 unit every 3 days as baseline for new products
            avg_daily_sales = 0.33
        
        if not avg_daily_sales:
            return None

        days_until_stockout = metrics.current_stock / max(avg_daily_sales, 1e-3)
        # Increased threshold from 14 to 30 days to catch more restock opportunities
        if days_until_stockout >= 30:
            return None

        # Adjusted priority levels: CRITICAL < 7, HIGH < 14, MEDIUM < 30
        if days_until_stockout < 7:
            priority = RecommendationPriority.CRITICAL
        elif days_until_stockout < 14:
            priority = RecommendationPriority.HIGH
        else:
            priority = RecommendationPriority.MEDIUM
        
        reorder_qty = self.calculate_reorder_quantity(metrics, avg_daily_sales)

        message = f"{metrics.product_name} will run out in {int(max(days_until_stockout, 1))} days - order now!"
        reasoning = (
            f"Current stock {metrics.current_stock} units, average daily sales {avg_daily_sales:.2f}. "
            f"Lead time {metrics.lead_time_days} days with safety stock {metrics.safety_stock}."
        )

        # Improved confidence calculation
        lower, upper = forecast.confidence_interval
        span = max(upper - lower, 0.0)
        forecast_uncertainty = span / max(upper, 1.0) if upper > 0 else 0.5

        # Factor in data availability and consistency
        data_quality = min(1.0, len(forecast.series) / 90.0)  # More data = higher confidence
        sales_consistency = 1.0 - min(0.5, metrics.avg_daily_sales_30d / max(avg_daily_sales, 1e-3) - 1.0)

        # Combined confidence score
        confidence = max(0.5, min(0.98,
            (1.0 - forecast_uncertainty * 0.4) *
            (data_quality * 0.3 + 0.7) *
            (sales_consistency * 0.3 + 0.7)
        ))

        return Recommendation(
            type=RecommendationType.URGENT_RESTOCK,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=priority,
            message=message,
            suggested_quantity=reorder_qty,
            current_stock=metrics.current_stock,
            days_until_stockout=days_until_stockout,
            confidence=confidence,
            reasoning=reasoning,
        )

    def check_trending(self, metrics: StockMetrics, signal: Optional[TrendSignal]) -> Optional[Recommendation]:
        if not signal or not signal.is_trending:
            return None
        # Increased stock target from 14 to 21 days to generate more recommendations
        additional = max(int(metrics.avg_daily_sales_7d * 21 - metrics.current_stock), 0)
        message = f"{metrics.product_name} sales up {signal.growth_rate * 100:.0f}% this week - stock up!"
        reasoning = (
            f"7-day avg {metrics.avg_daily_sales_7d:.2f} vs 30-day avg {metrics.avg_daily_sales_30d:.2f}. "
            "Trend flagged by anomaly detection."
        )
        return Recommendation(
            type=RecommendationType.TRENDING,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=RecommendationPriority.HIGH,
            message=message,
            suggested_quantity=additional if additional > 0 else None,
            current_stock=metrics.current_stock,
            growth_percentage=signal.growth_rate * 100,
            confidence=min(0.9, max(0.5, 0.7 + signal.stability_index / 3)),
            reasoning=reasoning,
        )

    def check_slow_mover(self, metrics: StockMetrics, signal: Optional[TrendSignal]) -> Optional[Recommendation]:
        if not signal or not signal.is_slow_mover:
            return None
        message = (
            f"{metrics.product_name} hasn't sold in {signal.days_since_last_sale} days - "
            "consider discount or bundling"
        )
        reasoning = (
            f"Inventory {metrics.current_stock} units with <0.5 average daily sales. "
            f"Holding cost estimate {metrics.holding_cost_per_day or 0:.2f} per day."
        )
        return Recommendation(
            type=RecommendationType.SLOW_MOVER,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=RecommendationPriority.MEDIUM,
            message=message,
            current_stock=metrics.current_stock,
            confidence=0.85,
            reasoning=reasoning,
        )

    def check_seasonal_forecast(self, metrics: StockMetrics) -> Optional[Recommendation]:
        seasonality = self.forecaster.detect_seasonality(metrics.sku)
        # Lowered threshold from 0.5 to 0.15 (15% lift) to detect more seasonal patterns
        if not seasonality or seasonality["seasonal_lift"] <= 0.15:
            return None
        lift = seasonality["seasonal_lift"]
        recommended_stock = int(max(float(metrics.current_stock), metrics.avg_daily_sales_30d * (1 + lift) * 30))
        additional = max(recommended_stock - metrics.current_stock, 0)
        if additional <= 0:
            return None
        message = (
            f"Historical data shows {lift * 100:.0f}% demand increase soon - prepare inventory."
        )
        reasoning = (
            f"Seasonal confidence {seasonality['confidence']:.2f}. "
            f"Baseline daily sales {metrics.avg_daily_sales_30d:.2f}."
        )
        return Recommendation(
            type=RecommendationType.SEASONAL,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=RecommendationPriority.MEDIUM,
            message=message,
            suggested_quantity=additional,
            current_stock=metrics.current_stock,
            confidence=float(seasonality["confidence"]),
            reasoning=reasoning,
        )

    def check_optimization_opportunity(self, metrics: StockMetrics) -> Optional[Recommendation]:
        """Identify products with good sales that could benefit from increased inventory."""
        # Target products with steady sales (at least 2 units/day) but relatively low stock
        if metrics.avg_daily_sales_30d < 2.0:
            return None
        
        days_of_stock = metrics.current_stock / max(metrics.avg_daily_sales_30d, 1e-3)
        # If stock is less than 45 days but more than 30 days, suggest optimization
        if days_of_stock >= 45 or days_of_stock < 30:
            return None
        
        optimal_stock = int(metrics.avg_daily_sales_30d * 60)  # Target 60 days
        additional = max(optimal_stock - metrics.current_stock, 0)
        
        if additional < 10:  # Only suggest if meaningful quantity
            return None
        
        message = (
            f"{metrics.product_name} has steady sales - consider increasing stock for better margin and availability."
        )
        reasoning = (
            f"Consistent daily sales of {metrics.avg_daily_sales_30d:.1f} units. "
            f"Current {days_of_stock:.0f} days of stock. Optimal target: 60 days for cost efficiency."
        )
        
        return Recommendation(
            type=RecommendationType.OPTIMIZATION,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=RecommendationPriority.LOW,
            message=message,
            suggested_quantity=additional,
            current_stock=metrics.current_stock,
            confidence=0.75,
            reasoning=reasoning,
        )

    def check_new_product(self, metrics: StockMetrics) -> Optional[Recommendation]:
        """Flag products with stock but no recent sales for monitoring."""
        # Only flag products with no sales in the last 30 days
        if metrics.avg_daily_sales_30d > 0:
            return None
        
        # Must have some inventory to be worth monitoring
        if metrics.current_stock < 5:
            return None
        
        message = (
            f"{metrics.product_name} has {metrics.current_stock} units in stock but no recent sales - "
            f"consider marketing push or review pricing."
        )
        reasoning = (
            f"Product has inventory ({metrics.current_stock} units) but zero sales in last 30 days. "
            f"May need visibility, promotion, or price adjustment to move inventory."
        )
        
        # Higher priority if lots of stock is sitting idle
        priority = RecommendationPriority.MEDIUM if metrics.current_stock > 50 else RecommendationPriority.LOW
        
        return Recommendation(
            type=RecommendationType.NEW_PRODUCT_MONITOR,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=priority,
            message=message,
            suggested_quantity=None,
            current_stock=metrics.current_stock,
            confidence=0.85,
            reasoning=reasoning,
        )

    def check_low_stock_alert(self, metrics: StockMetrics) -> Optional[Recommendation]:
        """Alert when stock falls below safety thresholds, regardless of sales."""
        # Skip if already handled by restock check
        if metrics.avg_daily_sales_30d > 0:
            days_coverage = metrics.current_stock / max(metrics.avg_daily_sales_30d, 1e-3)
            if days_coverage < 30:  # Already covered by restock
                return None
        
        # Alert on very low absolute stock levels
        if metrics.current_stock > 20:
            return None
        
        if metrics.current_stock == 0:
            return None  # Out of stock is different - not generating recs for 0 stock
        
        message = f"{metrics.product_name} is running low ({metrics.current_stock} units) - consider restocking soon."
        reasoning = (
            f"Stock level at {metrics.current_stock} units is below recommended threshold. "
            f"{'Low sales activity detected.' if metrics.avg_daily_sales_30d < 1 else 'Active sales require monitoring.'}"
        )
        
        priority = RecommendationPriority.HIGH if metrics.current_stock < 10 else RecommendationPriority.MEDIUM
        
        # Suggest bringing stock up to at least 30-50 units
        target_stock = 50 if metrics.avg_daily_sales_30d > 1 else 30
        suggested_qty = max(target_stock - metrics.current_stock, 10)
        
        return Recommendation(
            type=RecommendationType.URGENT_RESTOCK,
            sku=metrics.sku,
            product_name=metrics.product_name,
            priority=priority,
            message=message,
            suggested_quantity=suggested_qty,
            current_stock=metrics.current_stock,
            confidence=0.80,
            reasoning=reasoning,
        )

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _is_excluded(self, rec: Recommendation, excluded: Set[tuple[str, str]]) -> bool:
        """Check if recommendation should be excluded based on user preferences."""
        return (rec.sku, rec.type.value) in excluded

    def _try_alternative(self, original_rec: Recommendation, metrics: StockMetrics) -> Optional[Recommendation]:
        """Generate an alternative recommendation if original was dismissed."""
        alternative = self.preference_service.suggest_alternative_approach(
            sku=original_rec.sku,
            original_type=original_rec.type,
            product_name=original_rec.product_name,
            current_stock=original_rec.current_stock
        )

        if not alternative:
            logger.info(f"No alternative available for SKU {original_rec.sku} type {original_rec.type.value}")
            return None

        # Check if we should try this alternative
        if not self.preference_service.should_try_alternative(original_rec.sku, alternative["type"]):
            logger.info(f"Max alternatives reached for SKU {original_rec.sku}")
            return None

        # Record that we're trying an alternative
        self.preference_service.record_alternative_attempt(original_rec.sku, original_rec.type.value)

        # Create alternative recommendation
        alt_rec = Recommendation(
            type=RecommendationType(alternative["type"]),
            sku=original_rec.sku,
            product_name=original_rec.product_name,
            priority=RecommendationPriority.MEDIUM,  # Alternatives are medium priority
            message=alternative["message"],
            suggested_quantity=None,  # Alternative approaches may not have quantity
            current_stock=original_rec.current_stock,
            confidence=0.7,  # Alternatives have moderate confidence
            reasoning=f"Alternative approach: {alternative['reasoning']}. "
                     f"Original '{original_rec.type.value}' recommendation was previously dismissed."
        )

        logger.info(
            f"Generated alternative '{alternative['type']}' for SKU {original_rec.sku} "
            f"(original: '{original_rec.type.value}')"
        )

        return alt_rec

    def calculate_reorder_quantity(self, metrics: StockMetrics, avg_daily_sales: float) -> int:
        lead_time = metrics.lead_time_days or 14
        safety_stock = metrics.safety_stock or 0
        base = avg_daily_sales * lead_time + safety_stock
        target_stock = avg_daily_sales * 45  # Aim for 45 day supply
        desired_stock = max(base, target_stock)
        quantity = int(max(desired_stock - metrics.current_stock, 0))
        return quantity

    def _iter_products(self) -> List[Product]:
        stmt = select(Product)
        return self.db.execute(stmt).scalars().all()

    @staticmethod
    def _priority_bucket(priority: RecommendationPriority) -> int:
        order = {
            RecommendationPriority.CRITICAL: 4,
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 1,
        }
        return order.get(priority, 0)
