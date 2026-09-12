from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # local, api, csv
    description: Mapped[str | None] = mapped_column(Text)
    last_updated: Mapped[datetime | None] = mapped_column(onupdate=func.now())
    is_active: Mapped[int] = mapped_column(default=1)
    metadata_json: Mapped[str | None] = mapped_column(Text)  # JSON string for additional metadata
