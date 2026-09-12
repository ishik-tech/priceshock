from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RiskResponse(BaseModel):
    product_id: int
    product_name: str
    horizon_days: int
    risk_level: str  # LOW, MODERATE, HIGH, SEVERE
    probability_5pct: float
    probability_10pct: float
    probability_20pct: float
    expected_change_pct: float
    confidence: float
    calculated_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True