# sistema-inventarios/backend/app/api/api.py
from fastapi import APIRouter
from app.api.endpoints import products

api_router = APIRouter()

# Incluimos el router de productos bajo el prefijo /v1
api_router.include_router(products.router, prefix="/v1/productos", tags=["Productos"])