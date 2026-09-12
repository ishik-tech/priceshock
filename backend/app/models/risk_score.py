from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id"), nullable=True)
    horizon_days = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MODERATE, HIGH, SEVERE
    probability_5pct = Column(Float)  # Probability of >5% increase
    probability_10pct = Column(Float)  # Probability of >10% increase
    probability_20pct = Column(Float)  # Probability of >20% increase
    expected_change_pct = Column(Float)
    confidence = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)

    # Relationship
    product = relationship("Product")