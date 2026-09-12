
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price_observation import PriceObservationResponse
from app.schemas.product import ProductResponse
from app.services.data_service import DataService

router = APIRouter()


@router.get("/api/products", response_model=list[ProductResponse])
async def get_products(
    category: str | None = None,
    db: Session = Depends(get_db)
):
    """Get all products, optionally filtered by category"""
    data_service = DataService(db)
    products = data_service.get_products(category=category)
    return products


@router.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    data_service = DataService(db)
    product = data_service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/api/products/{product_id}/history", response_model=list[PriceObservationResponse])
async def get_product_history(
    product_id: int,
    days: int = Query(365, ge=30, le=3650),
    db: Session = Depends(get_db)
):
    """Get price history for a product"""
    from datetime import datetime, timedelta

    data_service = DataService(db)
    product = data_service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    observations = data_service.get_price_history(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )

    return observations
