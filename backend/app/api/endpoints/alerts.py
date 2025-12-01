import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

import app.services.alerts as alerts_service
from app.api.deps import get_db
from app.schemas.alerta import AlertaInDB # Nueva importacion

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/stock-minimo",
    response_model=List[AlertaInDB],
    summary="Obtener alertas de productos con stock bajo"
)
def get_low_stock_alerts(
    db: Session = Depends(get_db)
) -> List[AlertaInDB]:
    """
    Obtiene una lista de alertas de todos los productos que estan
    por debajo de su stock minimo.
    """
    logger.info("Procesando peticion de alerta de stock minimo...")
    try:
        alertas = alerts_service.get_alertas_activas_read(db=db, tipo_alerta="stock_minimo")
        return alertas
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error inesperado al obtener alertas de stock minimo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener alertas de stock mínimo.")


@router.get(
    "/por-vencer",
    response_model=List[AlertaInDB],
    summary="Obtener alertas de lotes proximos a vencer"
)
def get_expiring_lotes_alert(
    db: Session = Depends(get_db),
    days: int = Query(
        30, 
        gt=0, 
        description="Umbral de dias para la alerta"
    )
) -> List[AlertaInDB]:
    """
    Obtiene una lista de alertas de todos los lotes que estan
    por vencer dentro del umbral de dias especificado.
    """
    logger.info(
        f"Procesando peticion de alerta de lotes por vencer "
        f"(umbral: {days} dias)..."
    )
    try:
        alertas = alerts_service.get_alertas_activas_read(db=db, tipo_alerta=f"por_vencer_{days}", days_threshold=days)
        return alertas
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error inesperado al obtener alertas de lotes por vencer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener alertas de lotes por vencer.")