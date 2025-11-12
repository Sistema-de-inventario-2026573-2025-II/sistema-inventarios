import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

import app.services.alerts as alerts_service
import app.schemas.producto as product_schema
from app.api.deps import get_db
from app.schemas.lote import Lote

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/stock-minimo",
    response_model=List[product_schema.Producto],
    summary="Obtener productos con stock bajo"
)
def get_low_stock_alerts(
    db: Session = Depends(get_db)
) -> List[product_schema.Producto]:
    """
    Obtiene una lista de todos los productos que estan
    por debajo de su stock minimo.
    """
    logger.info("Procesando peticion de alerta de stock minimo...")
    products = alerts_service.check_stock_minimo(db=db)
    return products


@router.get(
    "/por-vencer",
    response_model=List[Lote],
    summary="Obtener lotes proximos a vencer"
)
def get_expiring_lotes_alert(
    db: Session = Depends(get_db),
    days: int = Query(
        30, 
        gt=0, 
        description="Umbral de dias para la alerta"
    )
) -> List[Lote]:
    """
    Obtiene una lista de todos los lotes que estan
    por vencer dentro del umbral de dias especificado.
    """
    logger.info(
        f"Procesando peticion de alerta de lotes por vencer "
        f"(umbral: {days} dias)..."
    )
    lotes = alerts_service.check_lotes_por_vencer(db=db, days_threshold=days)
    return lotes