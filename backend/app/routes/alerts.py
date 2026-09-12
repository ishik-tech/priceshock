from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.alert import AlertCreate, AlertResponse
from app.models.alert import Alert

router = APIRouter()


@router.post("/api/alerts", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(db: Session = Depends(get_db)):
    """Get all alerts"""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return alerts