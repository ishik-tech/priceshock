from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)  # local, api, csv
    description = Column(Text)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Integer, default=1)
    metadata_json = Column(Text)  # JSON string for additional metadata