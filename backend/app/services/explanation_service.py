import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.forecast_run import ForecastRun
from app.models.forecast_prediction import ForecastPrediction


class ExplanationService:
    """Service for generating forecast explanations"""

    def __init__(self, db: Session):
        self.db = db

    def get_feature_importance(self, product_id: int, model_name: str) -> Dict[str, float]:
        """Get feature importance for a model"""
        # This is a simplified version - in production, you'd load the actual model
        # and extract feature importance

        if model_name == "random_forest":
            return {
                "Historical momentum": 0.35,
                "Seasonality": 0.25,
                "30-day trend": 0.20,
                "Rolling average": 0.12,
                "External indicators": 0.08,
            }
        elif model_name == "arima":
            return {
                "AR terms": 0.40,
                "MA terms": 0.30,
                "Trend": 0.20,
                "Seasonal component": 0.10,
            }
        else:
            return {
                "Recent price": 1.0,
            }

    def explain_forecast(
        self,
        product_id: int,
        forecast_run_id: int
    ) -> Dict:
        """Generate explanation for a forecast"""

        forecast_run = self.db.query(ForecastRun).filter(
            ForecastRun.id == forecast_run_id
        ).first()

        if not forecast_run:
            return {"error": "Forecast not found"}

        # Get predictions
        predictions = self.db.query(ForecastPrediction).filter(
            ForecastPrediction.forecast_run_id == forecast_run_id
        ).order_by(ForecastPrediction.horizon_days).all()

        if not predictions:
            return {"error": "No predictions found"}

        # Get feature importance
        feature_importance = self.get_feature_importance(product_id, forecast_run.model_name)

        # Calculate contribution breakdown
        first_pred = predictions[0]
        last_pred = predictions[-1]

        total_change = last_pred.predicted_price - first_pred.predicted_price

        explanation = {
            "model_name": forecast_run.model_name,
            "total_predictions": len(predictions),
            "horizon_days": forecast_run.horizon_days,
            "feature_importance": feature_importance,
            "price_change_breakdown": {
                "total_change": round(total_change, 2),
                "change_percentage": round((total_change / first_pred.predicted_price) * 100, 2),
            },
            "key_factors": self._identify_key_factors(predictions, feature_importance),
            "confidence_factors": self._assess_confidence(predictions),
        }

        return explanation

    def _identify_key_factors(self, predictions: List[ForecastPrediction], feature_importance: Dict) -> List[str]:
        """Identify key factors driving the forecast"""
        factors = []

        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

        for feature, importance in sorted_features[:3]:
            if importance > 0.1:
                factors.append(feature)

        return factors

    def _assess_confidence(self, predictions: List[ForecastPrediction]) -> Dict:
        """Assess confidence in the forecast"""
        if len(predictions) < 2:
            return {"overall": "Low", "reason": "Insufficient predictions"}

        # Check prediction interval width
        intervals = []
        for pred in predictions:
            if pred.upper_bound and pred.lower_bound:
                interval_width = pred.upper_bound - pred.lower_bound
                relative_width = interval_width / pred.predicted_price if pred.predicted_price > 0 else 1
                intervals.append(relative_width)

        if not intervals:
            return {"overall": "Unknown", "reason": "No prediction intervals"}

        avg_interval = np.mean(intervals)

        if avg_interval < 0.1:
            confidence = "High"
            reason = "Tight prediction intervals"
        elif avg_interval < 0.2:
            confidence = "Moderate"
            reason = "Moderate prediction uncertainty"
        else:
            confidence = "Low"
            reason = "Wide prediction intervals indicate high uncertainty"

        return {
            "overall": confidence,
            "reason": reason,
            "avg_interval_width_pct": round(avg_interval * 100, 1),
        }