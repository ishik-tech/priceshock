from datetime import datetime

from pydantic import BaseModel


class ProductSummary(BaseModel):
    product_id: int
    product_name: str
    category: str
    current_price: float
    expected_30d_change_pct: float | None = None
    risk_level: str | None = None
    model_mae: float | None = None


class DashboardResponse(BaseModel):
    generated_at: datetime
    total_products: int
    total_forecasts: int
    high_risk_products: int
    average_model_mae: float
    data_source: str
    last_updated: datetime
    data_quality_score: float
    top_risk_products: list[ProductSummary]
    top_uncertainty_products: list[ProductSummary]
