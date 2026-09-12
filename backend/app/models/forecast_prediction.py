from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    forecast_run_id: Mapped[int] = mapped_column(ForeignKey("forecast_runs.id"), nullable=False, index=True)
    forecast_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    predicted_price: Mapped[float] = mapped_column(nullable=False)
    lower_bound: Mapped[float | None] = mapped_column()
    upper_bound: Mapped[float | None] = mapped_column()
    horizon_days: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
