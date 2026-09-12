from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    horizon_days = Column(Integer, nullable=False)
    run_date = Column(DateTime(timezone=True), server_default=func.now())
    mae = Column(Float)
    rmse = Column(Float)
    mape = Column(Float)
    coverage = Column(Float)  # Prediction interval coverage
    train_samples = Column(Integer)
    notes = Column(Text)