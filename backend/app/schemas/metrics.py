from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ModelMetricsSchema(BaseModel):
    model_name: str
    mae: float
    rmse: float
    mape: Optional[float] = None
    coverage: Optional[float] = None
    train_time_seconds: Optional[float] = None
    predict_time_seconds: Optional[float] = None
    is_baseline: bool
    sample_count: int
    evaluation_date: datetime

    class Config:
        from_attributes = True


class ModelComparison(BaseModel):
    product_id: int
    product_name: str
    models: List[ModelMetricsSchema]
    best_model: str
    improvement_vs_baseline_pct: Optional[float] = None


class ProductMetricsResponse(BaseModel):
    product_id: int
    product_name: str
    current_price: float
    data_points: int
    date_range_start: datetime
    date_range_end: datetime
    model_comparison: ModelComparison
    data_quality_score: float