import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.price_observation import PriceObservation
from app.models.data_source import DataSource
from app.schemas.price_observation import PriceObservationCreate


class DataService:
    """Service for managing price data"""

    def __init__(self, db: Session):
        self.db = db

    def get_products(self, category: Optional[str] = None) -> List[Product]:
        """Get all products, optionally filtered by category"""
        query = self.db.query(Product)

        if category:
            query = query.filter(Product.category == category)

        return query.all()

    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a single product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_price_history(
        self,
        product_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PriceObservation]:
        """Get price history for a product"""
        query = self.db.query(PriceObservation).filter(
            PriceObservation.product_id == product_id
        )

        if start_date:
            query = query.filter(PriceObservation.date >= start_date)
        if end_date:
            query = query.filter(PriceObservation.date <= end_date)

        return query.order_by(PriceObservation.date).all()

    def get_latest_price(self, product_id: int) -> Optional[PriceObservation]:
        """Get the most recent price observation"""
        return (
            self.db.query(PriceObservation)
            .filter(PriceObservation.product_id == product_id)
            .order_by(PriceObservation.date.desc())
            .first()
        )

    def add_price_observation(self, observation: PriceObservationCreate) -> PriceObservation:
        """Add a new price observation"""
        db_observation = PriceObservation(**observation.model_dump())
        self.db.add(db_observation)
        self.db.commit()
        self.db.refresh(db_observation)
        return db_observation

    def calculate_data_quality_score(self, product_id: int) -> float:
        """Calculate data quality score for a product (0-100)"""
        observations = self.db.query(PriceObservation).filter(
            PriceObservation.product_id == product_id
        ).all()

        if not observations:
            return 0.0

        score = 100.0
        penalties = 0

        # Check for missing values
        prices = [obs.price for obs in observations]
        if any(p <= 0 for p in prices):
            penalties += 20

        # Check for duplicates
        dates = [obs.date for obs in observations]
        if len(dates) != len(set(dates)):
            penalties += 15

        # Check for outliers (simple IQR method)
        if len(prices) >= 4:
            q1, q3 = np.percentile(prices, [25, 75])
            iqr = q3 - q1
            outliers = [p for p in prices if p < q1 - 1.5 * iqr or p > q3 + 1.5 * iqr]
            if len(outliers) > len(prices) * 0.1:  # More than 10% outliers
                penalties += 10

        # Check for stale data (no observations in last 30 days)
        latest_date = max(dates)
        if datetime.now() - latest_date > timedelta(days=30):
            penalties += 15

        # Check for sufficient data
        if len(observations) < 30:
            penalties += 20

        # Check for large jumps
        prices_sorted = sorted(prices)
        for i in range(1, len(prices_sorted)):
            jump = (prices_sorted[i] - prices_sorted[i-1]) / prices_sorted[i-1] if prices_sorted[i-1] > 0 else 0
            if abs(jump) > 0.5:  # 50% jump
                penalties += 5
                break

        score = max(0, score - penalties)
        return score

    def get_data_source_info(self) -> Dict:
        """Get information about current data source"""
        total_observations = self.db.query(PriceObservation).count()
        synthetic_count = self.db.query(PriceObservation).filter(
            PriceObservation.is_synthetic == True
        ).count()

        data_source = self.db.query(DataSource).first()

        return {
            "source_name": data_source.name if data_source else "Local Database",
            "source_type": data_source.source_type if data_source else "local",
            "total_observations": total_observations,
            "synthetic_count": synthetic_count,
            "is_synthetic": synthetic_count > 0,
            "last_updated": data_source.last_updated if data_source else datetime.now(),
        }