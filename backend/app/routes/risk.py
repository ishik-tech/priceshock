from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.risk import RiskResponse
from app.services.risk_service import RiskService
from app.services.data_service import DataService
from app.services.forecasting_service import ForecastingService
from datetime import datetime

router = APIRouter()


@router.get("/api/products/{product_id}/risk", response_model=RiskResponse)
async def get_product_risk(
    product_id: int,
    horizon_days: int = 90,
    db: Session = Depends(get_db)
):
    """Get risk assessment for a product"""

    # Validate product exists
    data_service = DataService(db)
    product = data_service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate forecast to get predictions
    forecasting_service = ForecastingService(db)
    forecast = forecasting_service.generate_forecast(
        product_id=product_id,
        horizon_days=horizon_days
    )

    if not forecast:
        raise HTTPException(
            status_code=422,
            detail="Insufficient historical data for risk assessment."
        )

    # Calculate risk
    risk_service = RiskService(db)
    risk = risk_service.calculate_risk(
        product_id=product_id,
        horizon_days=horizon_days,
        current_price=forecast["current_price"],
        predictions=forecast["predictions"]
    )

    return RiskResponse(
        product_id=product_id,
        product_name=product.name,
        horizon_days=horizon_days,
        risk_level=risk["risk_level"],
        probability_5pct=risk["probability_5pct"],
        probability_10pct=risk["probability_10pct"],
        probability_20pct=risk["probability_20pct"],
        expected_change_pct=risk["expected_change_pct"],
        confidence=risk["confidence"],
        calculated_at=datetime.now(),
    )


@router.get("/api/risk/top")
async def get_top_risk_products(
    limit: int = 10,
    horizon_days: int = 90,
    db: Session = Depends(get_db)
):
    """Get products with highest price rise risk"""
    risk_service = RiskService(db)
    top_risks = risk_service.get_top_risk_products(limit=limit, horizon_days=horizon_days)

    return {
        "horizon_days": horizon_days,
        "products": top_risks,
        "generated_at": datetime.now().isoformat(),
    }