# sistema-inventarios/backend/app/api/endpoints/reports.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import app.services.reports as reports_service
import app.schemas.producto as product_schema
from app.api.deps import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/inventario-basico",
    response_model=List[product_schema.Producto], # O un schema mas simple si solo se necesita lo basico
    summary="Reporte basico de inventario por producto"
)
def get_basic_inventory_report(
    db: Session = Depends(get_db)
) -> List[product_schema.Producto]:
    """
    Genera un reporte basico del inventario, mostrando el stock actual
    por cada producto.
    """
    logger.info("Generando reporte basico de inventario...")
    try:
        products = reports_service.get_current_stock_per_product(db=db)
        return products
    except Exception as e:
        logger.error(f"Error inesperado al generar reporte de inventario basico: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar reporte de inventario.")
