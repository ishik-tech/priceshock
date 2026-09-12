from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ProductSummary(BaseModel):
    product_id: int
    product_name: str
    category: str
    current_price: float
    expected_30d_change_pct: Optional[float] = None
    risk_level: Optional[str] = None
    model_mae: Optional[float] = None


class DashboardResponse(BaseModel):
    generated_at: datetime
    total_products: int
    total_forecasts: int
    high_risk_products: int
    average_model_mae: float
    data_source: str
    last_updated: datetime
    data_quality_score: float
    top_risk_products: List[ProductSummary]
    top_uncertainty_products: List[ProductSummary]