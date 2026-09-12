from datetime import datetime

from pydantic import BaseModel


class ForecastPredictionSchema(BaseModel):
    forecast_date: datetime
    predicted_price: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    horizon_days: int

    class Config:
        from_attributes = True


class ForecastRequest(BaseModel):
    product_id: int
    horizon_days: int = 30  # 7, 30, 90, 180
    model_name: str | None = None  # Auto-select if None


class ForecastResponse(BaseModel):
    product_id: int
    product_name: str
    model_used: str
    horizon_days: int
    current_price: float
    predictions: list[ForecastPredictionSchema]
    expected_change_pct: float
    data_quality_score: float
    forecast_generated_at: datetime
    is_synthetic_data: bool

    class Config:
        from_attributes = True
