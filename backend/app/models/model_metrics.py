from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    evaluation_date: Mapped[datetime | None] = mapped_column(server_default=func.now())
    mae: Mapped[float] = mapped_column(nullable=False)
    rmse: Mapped[float] = mapped_column(nullable=False)
    mape: Mapped[float | None] = mapped_column()
    coverage: Mapped[float | None] = mapped_column()
    train_time_seconds: Mapped[float | None] = mapped_column()
    predict_time_seconds: Mapped[float | None] = mapped_column()
    is_baseline: Mapped[int] = mapped_column(default=0)  # 1 if baseline model
    sample_count: Mapped[int | None] = mapped_column()
