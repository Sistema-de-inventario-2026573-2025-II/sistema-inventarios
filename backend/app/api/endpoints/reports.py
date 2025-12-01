# sistema-inventarios/backend/app/api/endpoints/reports.py
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date # Nueva importacion

import app.services.reports as reports_service
import app.schemas.producto as product_schema
import app.schemas.lote as lote_schema # Importar el schema de lote
import app.schemas.movimiento as movimiento_schema # Nueva importacion


from app.api.deps import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/top-productos-disponibles",
    response_model=List[product_schema.Producto], # O un schema mas simple si solo se necesita lo basico
    summary="Reporte de los productos con mayor disponibilidad"
)
def get_top_available_products_report(
    db: Session = Depends(get_db),
    top_n: int = Query(
        5,
        gt=0,
        le=100,
        description="Numero de productos a incluir en el reporte"
    )
) -> List[product_schema.Producto]:
    """
    Genera un reporte de los N productos con mayor cantidad_actual en inventario.
    """
    logger.info(f"Generando reporte de top {top_n} productos disponibles...")
    try:
        top_products = reports_service.get_top_available_products(db=db, top_n=top_n)
        return top_products
    except Exception as e:
        logger.error(f"Error inesperado al generar reporte de productos disponibles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar reporte de productos disponibles.")

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

@router.get(
    "/lotes-por-vencer",
    response_model=List[lote_schema.Lote], # Usar el schema de lote
    summary="Reporte de lotes proximos a vencer"
)
def get_expiring_lotes_report(
    db: Session = Depends(get_db),
    days_threshold: int = Query(
        30,
        gt=0,
        description="Numero de dias para considerar un lote proximo a vencer"
    )
) -> List[lote_schema.Lote]: # Corregido a lote_schema.Lote
    """
    Genera un reporte de lotes que estan proximos a vencer dentro del umbral
    de dias especificado.
    """
    logger.info(f"Generando reporte de lotes por vencer (umbral: {days_threshold} dias)...")
    try:
        lotes = reports_service.get_expiring_lotes_report(db=db, days_threshold=days_threshold)
        return lotes
    except Exception as e:
        logger.error(f"Error inesperado al generar reporte de lotes por vencer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar reporte de lotes por vencer.")

@router.get(
    "/movimientos-por-rango-fecha",
    response_model=List[movimiento_schema.Movimiento], # Usar el schema de movimiento
    summary="Reporte de movimientos de inventario por rango de fecha"
)
def get_movement_report(
    db: Session = Depends(get_db),
    fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
) -> List[movimiento_schema.Movimiento]:
    """
    Genera un reporte de todos los movimientos de inventario (entradas y salidas)
    dentro de un rango de fechas especificado.
    """
    logger.info(f"Generando reporte de movimientos entre {fecha_inicio} y {fecha_fin}...")
    try:
        movimientos = reports_service.get_movement_report_by_date_range(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return movimientos
    except Exception as e:
        logger.error(f"Error inesperado al generar reporte de movimientos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar reporte de movimientos.")
