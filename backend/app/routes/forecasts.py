from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.data_service import DataService
from app.services.forecasting_service import ForecastingService
from app.services.risk_service import RiskService

router = APIRouter()


@router.post("/api/products/{product_id}/forecast", response_model=ForecastResponse)
async def generate_forecast(
    product_id: int,
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """Generate price forecast for a product"""

    # Validate product exists
    data_service = DataService(db)
    product = data_service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate horizon
    if request.horizon_days not in [7, 30, 90, 180]:
        raise HTTPException(
            status_code=400,
            detail="Horizon must be 7, 30, 90, or 180 days"
        )

    # Generate forecast
    forecasting_service = ForecastingService(db)
    forecast_result = forecasting_service.generate_forecast(
        product_id=product_id,
        horizon_days=request.horizon_days,
        model_name=request.model_name
    )

    if not forecast_result:
        raise HTTPException(
            status_code=422,
            detail="Insufficient historical data for a reliable forecast."
        )

    # Calculate risk (persisted as a side effect for dashboard/top-risk queries)
    risk_service = RiskService(db)
    risk_service.calculate_risk(
        product_id=product_id,
        horizon_days=request.horizon_days,
        current_price=forecast_result["current_price"],
        predictions=forecast_result["predictions"]
    )

    # Get data quality
    data_quality = data_service.calculate_data_quality_score(product_id)

    # Check if data is synthetic
    latest_obs = data_service.get_latest_price(product_id)
    is_synthetic = latest_obs.is_synthetic if latest_obs else True

    return ForecastResponse(
        product_id=product_id,
        product_name=product.name,
        model_used=forecast_result["model_used"],
        horizon_days=forecast_result["horizon_days"],
        current_price=forecast_result["current_price"],
        predictions=forecast_result["predictions"],
        expected_change_pct=forecast_result["expected_change_pct"],
        data_quality_score=data_quality,
        forecast_generated_at=datetime.now(),
        is_synthetic_data=is_synthetic,
    )
