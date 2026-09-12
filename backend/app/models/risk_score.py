from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    forecast_run_id: Mapped[int | None] = mapped_column(ForeignKey("forecast_runs.id"), nullable=True)
    horizon_days: Mapped[int] = mapped_column(nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW, MODERATE, HIGH, SEVERE
    probability_5pct: Mapped[float | None] = mapped_column()  # Probability of >5% increase
    probability_10pct: Mapped[float | None] = mapped_column()  # Probability of >10% increase
    probability_20pct: Mapped[float | None] = mapped_column()  # Probability of >20% increase
    expected_change_pct: Mapped[float | None] = mapped_column()
    confidence: Mapped[float | None] = mapped_column()
    calculated_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationship
    product = relationship("Product")
