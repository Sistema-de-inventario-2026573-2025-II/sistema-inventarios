# sistema-inventarios/backend/app/services/alerts.py
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date, timedelta

from app.models.producto import Producto as ProductoModel
from app.models.lote import Lote as LoteModel
from app.models.alerta import Alerta # Nueva importacion
from app.schemas.producto import Producto as ProductoSchema
from app.schemas.lote import Lote as LoteSchema
from app.schemas.alerta import AlertaCreate # Nueva importacion
from app.crud import crud_alerta # Nueva importacion
from app.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY_STOCK_MINIMO = "alert_stock_minimo"
CACHE_KEY_LOTES_VENCIMIENTO = "alert_lotes_vencimiento"

def check_stock_minimo(db: Session) -> None:
    """
    Servicio que gestiona las alertas de productos por debajo de su stock minimo.
    Crea nuevas alertas o desactiva existentes segun sea necesario.
    """
    logger.info("Gestionando alertas de stock minimo...")

    # 1. Obtener todos los productos que estan actualmente por debajo de su stock minimo
    productos_bajo_stock_actual = db.scalars(
        select(ProductoModel)
        .where(ProductoModel.cantidad_actual < ProductoModel.stock_minimo)
    ).all()
    
    productos_ids_bajo_stock_actual = {p.id for p in productos_bajo_stock_actual}

    # 2. Obtener todas las alertas de stock minimo activas actualmente en la BD
    alertas_activas_db = db.scalars(
        select(Alerta)
        .where(
            Alerta.tipo_alerta == "stock_minimo",
            Alerta.entidad_tipo == "producto",
            Alerta.esta_activa == True
        )
    ).all()
    
    alertas_activas_por_producto_id = {a.entidad_id: a for a in alertas_activas_db}

    # 3. Crear nuevas alertas para productos que ahora estan bajo stock y no tienen alerta activa
    for producto in productos_bajo_stock_actual:
        if producto.id not in alertas_activas_por_producto_id:
            mensaje = (
                f"El producto '{producto.nombre}' (SKU: {producto.sku}) "
                f"tiene {producto.cantidad_actual} unidades, por debajo del stock "
                f"minimo de {producto.stock_minimo}."
            )
            crud_alerta.create_alerta(
                db=db,
                alerta=AlertaCreate(
                    tipo_alerta="stock_minimo",
                    entidad_id=producto.id,
                    entidad_tipo="producto",
                    mensaje=mensaje,
                    metadata_json={
                        "nombre": producto.nombre,
                        "sku": producto.sku,
                        "cantidad_actual": producto.cantidad_actual,
                        "stock_minimo": producto.stock_minimo,
                    }
                )
            )
            logger.warning(f"Nueva alerta de stock minimo creada para Producto ID: {producto.id}")

    # 4. Desactivar alertas para productos que ya NO estan bajo stock
    for entidad_id, alerta_activa in alertas_activas_por_producto_id.items():
        if entidad_id not in productos_ids_bajo_stock_actual:
            crud_alerta.deactivate_alerta(db=db, alerta_id=alerta_activa.id)
            logger.info(f"Alerta de stock minimo desactivada para Producto ID: {entidad_id}")

    # Invalidar cache de alertas de stock minimo para asegurar que se consulte la BD
    cache.invalidate_pattern(CACHE_KEY_STOCK_MINIMO)

    logger.info("Gestion de alertas de stock minimo finalizada.")

def check_lotes_por_vencer_and_manage_alerts(db: Session, *, days_threshold: int = 30) -> None:
    """
    Servicio que gestiona las alertas de lotes proximos a vencer.
    Crea nuevas alertas o desactiva existentes segun sea necesario.
    """
    logger.info(f"Gestionando alertas de lotes por vencer (umbral: {days_threshold} dias)...")

    # 1. Obtener todos los lotes que estan actualmente por vencer
    today = date.today()
    target_date = today + timedelta(days=days_threshold)
    
    lotes_por_vencer_actual = db.scalars(
        select(LoteModel)
        .where(
            and_(
                LoteModel.fecha_vencimiento.isnot(None),
                LoteModel.cantidad_actual > 0,
                LoteModel.fecha_vencimiento > today,
                LoteModel.fecha_vencimiento <= target_date
            )
        )
    ).all()
    
    lotes_ids_por_vencer_actual = {l.id for l in lotes_por_vencer_actual}

    # 2. Obtener todas las alertas de lotes por vencer activas actualmente en la BD
    alertas_activas_db = db.scalars(
        select(Alerta)
        .where(
            Alerta.tipo_alerta == f"por_vencer_{days_threshold}",
            Alerta.entidad_tipo == "lote",
            Alerta.esta_activa == True
        )
    ).all()
    
    alertas_activas_por_lote_id = {a.entidad_id: a for a in alertas_activas_db}

    # 3. Crear nuevas alertas para lotes que ahora estan por vencer y no tienen alerta activa
    for lote in lotes_por_vencer_actual:
        if lote.id not in alertas_activas_por_lote_id:
            mensaje = (
                f"El lote ID {lote.id} del producto '{lote.producto.nombre}' (SKU: {lote.producto.sku}) "
                f"tiene {lote.cantidad_actual} unidades y vence el {lote.fecha_vencimiento}."
            )
            crud_alerta.create_alerta(
                db=db,
                alerta=AlertaCreate(
                    tipo_alerta=f"por_vencer_{days_threshold}",
                    entidad_id=lote.id,
                    entidad_tipo="lote",
                    mensaje=mensaje,
                    metadata_json={
                        "producto_nombre": lote.producto.nombre,
                        "producto_sku": lote.producto.sku,
                        "cantidad_actual": lote.cantidad_actual,
                        "fecha_vencimiento": str(lote.fecha_vencimiento),
                    }
                )
            )
            logger.warning(f"Nueva alerta de lote por vencer creada para Lote ID: {lote.id}")

    # 4. Desactivar alertas para lotes que ya NO estan por vencer
    for entidad_id, alerta_activa in alertas_activas_por_lote_id.items():
        if entidad_id not in lotes_ids_por_vencer_actual:
            crud_alerta.deactivate_alerta(db=db, alerta_id=alerta_activa.id)
            logger.info(f"Alerta de lote por vencer desactivada para Lote ID: {entidad_id}")

    # Invalidar cache de alertas de lotes por vencer para asegurar que se consulte la BD
    cache.invalidate_pattern(f"{CACHE_KEY_LOTES_VENCIMIENTO}_{days_threshold}")

    logger.info("Gestion de alertas de lotes por vencer finalizada.")

def get_alertas_activas_read(db: Session, tipo_alerta: Optional[str] = None, days_threshold: Optional[int] = None) -> List[Alerta]:
    """
    Servicio de lectura que devuelve todas las alertas activas,
    opcionalmente filtradas por tipo de alerta.
    Antes de devolver las alertas, se asegura de que la tabla de alertas esté actualizada.
    """
    logger.info("Solicitud de lectura de alertas activas. Actualizando tabla de alertas primero...")
    check_stock_minimo(db)
    # Ejecutar la gestion de lotes por vencer con un umbral por defecto si no se especifica
    if days_threshold:
        check_lotes_por_vencer_and_manage_alerts(db, days_threshold=days_threshold)
    else:
        # Se puede ejecutar con un umbral por defecto o todos los umbrales relevantes
        # Por ahora, usamos 30 dias como umbral por defecto si no se da ninguno.
        check_lotes_por_vencer_and_manage_alerts(db, days_threshold=30) 
        # Considerar si se necesitan otros umbrales (ej. 7, 15, 60 días)

    return crud_alerta.get_active_alertas(db, tipo_alerta=tipo_alerta)