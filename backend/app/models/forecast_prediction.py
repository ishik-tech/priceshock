from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id = Column(Integer, primary_key=True, index=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id"), nullable=False, index=True)
    forecast_date = Column(DateTime, nullable=False)
    predicted_price = Column(Float, nullable=False)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    horizon_days = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())