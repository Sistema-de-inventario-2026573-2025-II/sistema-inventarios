# sistema-inventarios/backend/app/services/reports.py
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.models.producto import Producto as ProductoModel
from app.schemas.producto import Producto as ProductoSchema # Usar el schema de producto directamente

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