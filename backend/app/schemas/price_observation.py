from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PriceObservationBase(BaseModel):
    product_id: int
    date: datetime
    price: float
    currency: str = "INR"
    unit: str
    region: str = "National"
    source: str
    is_synthetic: bool = False


class PriceObservationCreate(PriceObservationBase):
    pass


class PriceObservationResponse(PriceObservationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True