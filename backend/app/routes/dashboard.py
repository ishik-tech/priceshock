from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.forecast_run import ForecastRun
from app.models.model_metrics import ModelMetrics
from app.models.risk_score import RiskScore
from app.schemas.dashboard import DashboardResponse, ProductSummary
from app.services.data_service import DataService
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard summary data"""

    data_service = DataService(db)
    risk_service = RiskService(db)

    # Get basic stats
    products = data_service.get_products()
    total_products = len(products)

    # Count forecasts
    forecast_count = db.query(ForecastRun).count()

    # Get high risk products
    high_risk_products = db.query(RiskScore).filter(
        RiskScore.risk_level.in_(["HIGH", "SEVERE"])
    ).count()

    # Calculate average model MAE
    avg_mae = db.query(func.avg(ModelMetrics.mae)).scalar()
    avg_mae = float(avg_mae) if avg_mae else 0.0

    # Get data source info
    data_source_info = data_service.get_data_source_info()

    # Get data quality score
    quality_scores = [data_service.calculate_data_quality_score(p.id) for p in products]
    data_quality_score = float(np.mean(quality_scores)) if quality_scores else 0.0

    # Get top risk products
    top_risk = risk_service.get_top_risk_products(limit=10, horizon_days=90)
    top_risk_products = [
        ProductSummary(
            product_id=r["product_id"],
            product_name=r["product_name"],
            category=r["category"],
            current_price=0.0,  # Would fetch from DB
            risk_level=r["risk_level"],
        )
        for r in top_risk[:5]
    ]

    # Get top uncertainty products (simplified - would use prediction interval width)
    top_uncertainty = top_risk[:5]
    top_uncertainty_products = [
        ProductSummary(
            product_id=r["product_id"],
            product_name=r["product_name"],
            category=r["category"],
            current_price=0.0,
        )
        for r in top_uncertainty
    ]

    return DashboardResponse(
        generated_at=datetime.now(),
        total_products=total_products,
        total_forecasts=forecast_count,
        high_risk_products=high_risk_products,
        average_model_mae=avg_mae,
        data_source=data_source_info["source_name"],
        last_updated=data_source_info["last_updated"],
        data_quality_score=data_quality_score,
        top_risk_products=top_risk_products,
        top_uncertainty_products=top_uncertainty_products,
    )
