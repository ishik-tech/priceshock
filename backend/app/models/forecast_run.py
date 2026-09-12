from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    horizon_days: Mapped[int] = mapped_column(nullable=False)
    run_date: Mapped[datetime | None] = mapped_column(server_default=func.now())
    mae: Mapped[float | None] = mapped_column()
    rmse: Mapped[float | None] = mapped_column()
    mape: Mapped[float | None] = mapped_column()
    coverage: Mapped[float | None] = mapped_column()  # Prediction interval coverage
    train_samples: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)
