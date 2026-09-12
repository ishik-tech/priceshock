from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    product_id: int
    alert_type: str  # probability_increase, expected_change, threshold_price
    threshold_value: float
    horizon_days: int
    condition: str  # greater_than, less_than, equals


class AlertResponse(BaseModel):
    id: int
    product_id: int
    alert_type: str
    threshold_value: float
    horizon_days: int
    condition: str
    is_active: bool
    created_at: datetime
    last_triggered: datetime | None = None

    class Config:
        from_attributes = True
