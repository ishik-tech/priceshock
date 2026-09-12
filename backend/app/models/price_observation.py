from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    unit = Column(String(50), nullable=False)
    region = Column(String(100), default="National")
    source = Column(String(200), nullable=False)
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    product = relationship("Product", back_populates="observations")


# Add relationship to Product
from app.models.product import Product
Product.observations = relationship("PriceObservation", order_by=PriceObservation.date, back_populates="product")