import numpy as np
import math
from typing import Dict
from sqlalchemy.orm import Session

from app.models.risk_score import RiskScore


class RiskService:
    """Service for calculating price rise risk"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_risk(
        self,
        product_id: int,
        horizon_days: int = 90,
        current_price: float = None,
        predictions: list = None
    ) -> Dict:
        """Calculate price rise risk for a product"""

        if not predictions or len(predictions) == 0:
            return {
                "risk_level": "UNKNOWN",
                "probability_5pct": 0.0,
                "probability_10pct": 0.0,
                "probability_20pct": 0.0,
                "expected_change_pct": 0.0,
                "confidence": 0.0,
            }

        # Get final prediction
        final_pred = predictions[-1]
        final_price = final_pred["predicted_price"]

        # Calculate expected change
        expected_change_pct = ((final_price - current_price) / current_price) * 100

        # Get prediction intervals to estimate distribution
        lower_bounds = [p.get("lower_bound", p["predicted_price"]) for p in predictions]
        upper_bounds = [p.get("upper_bound", p["predicted_price"]) for p in predictions]

        # Estimate volatility from prediction intervals
        avg_interval_width = np.mean([ub - lb for ub, lb in zip(upper_bounds, lower_bounds)])
        relative_volatility = avg_interval_width / current_price if current_price > 0 else 1.0

        # Calculate probabilities based on forecast distribution
        # Using simplified approach based on expected change and volatility
        mean_change = expected_change_pct
        std_change = relative_volatility * 100 / 2  # Approximate std from CI

        # Probability calculations using normal distribution approximation
        prob_5pct = self._calculate_threshold_probability(mean_change, std_change, 5)
        prob_10pct = self._calculate_threshold_probability(mean_change, std_change, 10)
        prob_20pct = self._calculate_threshold_probability(mean_change, std_change, 20)

        # Determine risk level
        if prob_10pct >= 0.7 or expected_change_pct >= 15:
            risk_level = "SEVERE"
        elif prob_10pct >= 0.5 or expected_change_pct >= 10:
            risk_level = "HIGH"
        elif prob_10pct >= 0.3 or expected_change_pct >= 5:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Calculate confidence (inverse of volatility)
        confidence = max(0, min(1, 1 - relative_volatility))

        result = {
            "risk_level": risk_level,
            "probability_5pct": round(prob_5pct, 3),
            "probability_10pct": round(prob_10pct, 3),
            "probability_20pct": round(prob_20pct, 3),
            "expected_change_pct": round(expected_change_pct, 2),
            "confidence": round(confidence, 2),
        }

        # Save to database
        risk_score = RiskScore(
            product_id=product_id,
            horizon_days=horizon_days,
            risk_level=risk_level,
            probability_5pct=prob_5pct,
            probability_10pct=prob_10pct,
            probability_20pct=prob_20pct,
            expected_change_pct=expected_change_pct,
            confidence=confidence,
        )
        self.db.add(risk_score)
        self.db.commit()

        return result

    def _calculate_threshold_probability(self, mean: float, std: float, threshold: float) -> float:
        """Calculate probability of exceeding threshold using normal distribution"""
        if std <= 0:
            return 1.0 if mean > threshold else 0.0

        # Z-score
        z = (threshold - mean) / std
        # Probability of exceeding threshold (upper tail)
        prob = 1 - self._normal_cdf(z)

        return max(0, min(1, prob))

    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF using error function"""
        return 0.5 * (1 + math.erf(x / np.sqrt(2)))

    def get_top_risk_products(self, limit: int = 10, horizon_days: int = 90) -> list:
        """Get products with highest price rise risk"""
        risk_scores = (
            self.db.query(RiskScore)
            .filter(RiskScore.horizon_days == horizon_days)
            .order_by(RiskScore.probability_10pct.desc())
            .limit(limit)
            .all()
        )

        results = []
        for risk in risk_scores:
            product = risk.product
            results.append({
                "product_id": risk.product_id,
                "product_name": product.name if product else "Unknown",
                "category": product.category if product else "Unknown",
                "risk_level": risk.risk_level,
                "probability_10pct": risk.probability_10pct,
                "expected_change_pct": risk.expected_change_pct,
                "horizon_days": risk.horizon_days,
            })

        return results