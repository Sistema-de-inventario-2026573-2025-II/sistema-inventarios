# sistema-inventarios/backend/app/api/api.py
from fastapi import APIRouter
from app.api.endpoints import products
from app.api.endpoints import inventory
from app.api.endpoints import alerts
from app.api.endpoints import reports # Nueva importacion

api_router = APIRouter()

# Incluimos el router de productos bajo el prefijo /v1
api_router.include_router(
    products.router,
    prefix="/v1/productos",
    tags=["Productos"])
api_router.include_router(
    inventory.router, 
    prefix="/v1/inventario",
    tags=["Inventario"] 
)
api_router.include_router(
    alerts.router,
    prefix="/v1/alertas",
    tags=["Alertas"]
)
api_router.include_router(
    reports.router,
    prefix="/v1/reportes",
    tags=["Reportes"]
)