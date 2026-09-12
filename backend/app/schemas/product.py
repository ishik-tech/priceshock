from datetime import datetime

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    category: str
    unit: str
    region: str = "National"
    description: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
