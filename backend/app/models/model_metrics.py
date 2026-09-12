from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    evaluation_date = Column(DateTime(timezone=True), server_default=func.now())
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    mape = Column(Float)
    coverage = Column(Float)
    train_time_seconds = Column(Float)
    predict_time_seconds = Column(Float)
    is_baseline = Column(Integer, default=0)  # 1 if baseline model
    sample_count = Column(Integer)