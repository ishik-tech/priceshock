from datetime import datetime

from pydantic import BaseModel


class ModelMetricsSchema(BaseModel):
    model_name: str
    mae: float
    rmse: float
    mape: float | None = None
    coverage: float | None = None
    train_time_seconds: float | None = None
    predict_time_seconds: float | None = None
    is_baseline: bool
    sample_count: int
    evaluation_date: datetime

    class Config:
        from_attributes = True


class ModelComparison(BaseModel):
    product_id: int
    product_name: str
    models: list[ModelMetricsSchema]
    best_model: str
    improvement_vs_baseline_pct: float | None = None


class ProductMetricsResponse(BaseModel):
    product_id: int
    product_name: str
    current_price: float
    data_points: int
    date_range_start: datetime
    date_range_end: datetime
    model_comparison: ModelComparison
    data_quality_score: float
