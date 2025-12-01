# sistema-inventarios/backend/app/services/reports.py
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from typing import List
from datetime import date, timedelta

from app.models.producto import Producto as ProductoModel
from app.models.lote import Lote as LoteModel 
from app.models.movimiento import Movimiento as MovimientoModel # Nueva importacion
from app.schemas.producto import Producto as ProductoSchema 
from app.schemas.lote import Lote as LoteSchema 
from app.schemas.movimiento import Movimiento as MovimientoSchema # Nueva importacion

logger = logging.getLogger(__name__)

def get_current_stock_per_product(db: Session) -> List[ProductoSchema]:
    """
    Servicio que devuelve el stock actual de todos los productos.
    """
    logger.info("Obteniendo stock actual por producto...")
    productos_orm = db.scalars(select(ProductoModel)).all()
    
    # Convertir a Pydantic Schema para asegurar que los datos sean serializables
    # y no arrastren objetos ORM.
    productos_schemas = [ProductoSchema.model_validate(p) for p in productos_orm]
    
    logger.info(f"Reporte de stock generado para {len(productos_schemas)} productos.")
    return productos_schemas

def get_expiring_lotes_report(db: Session, *, days_threshold: int = 30) -> List[LoteSchema]:
    """
    Servicio que devuelve una lista de lotes que estan por vencer,
    incluyendo la informacion del producto asociado.
    """
    logger.info(f"Generando reporte de lotes por vencer (umbral: {days_threshold} dias)...")
    today = date.today()
    target_date = today + timedelta(days=days_threshold)
    
    stmt = select(LoteModel).options(joinedload(LoteModel.producto)).where(
        and_(
            LoteModel.fecha_vencimiento.isnot(None),
            LoteModel.cantidad_actual > 0,
            LoteModel.fecha_vencimiento > today,
            LoteModel.fecha_vencimiento <= target_date
        )
    ).order_by(LoteModel.fecha_vencimiento.asc())

    lotes_orm = db.scalars(stmt).all()

    # Convertir a Pydantic Schema, incluyendo el producto
    lotes_schemas = [LoteSchema.model_validate(l) for l in lotes_orm]
    
    logger.info(f"Reporte de lotes por vencer generado para {len(lotes_schemas)} lotes.")
    return lotes_schemas

def get_movement_report_by_date_range(db: Session, fecha_inicio: date, fecha_fin: date) -> List[MovimientoSchema]:
    """
    Servicio que devuelve una lista de movimientos de inventario dentro de un rango de fechas,
    incluyendo la informacion del producto y lote asociado.
    """
    logger.info(f"Generando reporte de movimientos entre {fecha_inicio} y {fecha_fin}...")

    stmt = select(MovimientoModel)\
        .options(
            joinedload(MovimientoModel.producto),
            joinedload(MovimientoModel.lote)
        )\
        .where(
            MovimientoModel.fecha_movimiento >= fecha_inicio,
            MovimientoModel.fecha_movimiento <= fecha_fin
        )\
        .order_by(MovimientoModel.fecha_movimiento.asc())
    
    movimientos_orm = db.scalars(stmt).all()

    # Convertir a Pydantic Schema, incluyendo las relaciones
    movimientos_schemas = [MovimientoSchema.model_validate(m) for m in movimientos_orm]

    logger.info(f"Reporte de movimientos generado para {len(movimientos_schemas)} movimientos.")
    return movimientos_schemas