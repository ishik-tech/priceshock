from app.routes.products import router as products_router
from app.routes.forecasts import router as forecasts_router
from app.routes.risk import router as risk_router
from app.routes.dashboard import router as dashboard_router
from app.routes.alerts import router as alerts_router
from app.routes.health import router as health_router

__all__ = [
    "products_router",
    "forecasts_router",
    "risk_router",
    "dashboard_router",
    "alerts_router",
    "health_router",
]