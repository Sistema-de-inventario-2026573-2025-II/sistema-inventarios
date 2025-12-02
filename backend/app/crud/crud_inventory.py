# sistema-inventarios/backend/app/crud/crud_inventory.py
import logging
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.models.lote import Lote
from app.models.movimiento import Movimiento
from app.schemas.lote import LoteCreate
from app.schemas.inventory import InventoryExitRequest, SmartDispatchReq
import app.crud.crud_product as crud_product
from app.core.exceptions import InsufficientStockError
from typing import List

logger = logging.getLogger(__name__)

def get_lotes(db: Session, skip: int = 0, limit: int = 100) -> List[Lote]:
    """
    Obtiene una lista de lotes, eager-cargando la informacion del producto.
    """
    logger.debug(f"Obteniendo lotes: skip={skip}, limit={limit}")
    return db.query(Lote).offset(skip).limit(limit).all()

def get_lote(db: Session, lote_id: int) -> Lote | None:
    """
    Obtiene un lote por su ID.
    """
    logger.debug(f"Buscando lote con id: {lote_id}")
    return db.query(Lote).filter(Lote.id == lote_id).first()

def register_entry(db: Session, *, entry_in: LoteCreate) -> Lote | None:
    """
    Registra una entrada de inventario, creando un Lote, un Movimiento
    y actualizando el stock del Producto.
    """
    logger.info(
        f"Registrando entrada de {entry_in.cantidad_recibida} "
        f"unidades para producto_id: {entry_in.producto_id}"
    )

    # 1. Obtener el producto (usamos el CRUD de producto existente)
    db_product = crud_product.get_product(db, product_id=entry_in.producto_id)
    if not db_product:
        logger.warning(f"Producto no encontrado: {entry_in.producto_id}")
        return None

    # 2. Crear el Lote
    # El modelo Lote se encarga de: self.cantidad_actual = self.cantidad_recibida
    db_lote = Lote(
        producto_id=entry_in.producto_id,
        cantidad_recibida=entry_in.cantidad_recibida,
        fecha_vencimiento=entry_in.fecha_vencimiento
    )
    
    # 3. Añadir el lote y hacer flush para obtener su ID
    # flush() envia el SQL a la BD pero no comitea la transaccion
    db.add(db_lote)
    db.flush() 
    logger.debug(f"Lote creado con id: {db_lote.id}")

    # 4. Crear el Movimiento
    db_movimiento = Movimiento(
        lote_id=db_lote.id,
        tipo="entrada",
        cantidad=entry_in.cantidad_recibida
    )
    
    # 5. Actualizar el stock del Producto
    stock_anterior = db_product.cantidad_actual
    db_product.cantidad_actual += entry_in.cantidad_recibida
    
    # 6. Añadir los objetos restantes a la sesion y comitear la transaccion
    db.add(db_movimiento)
    db.add(db_product)
    db.commit()
    
    logger.info(
        f"Entrada registrada para lote id: {db_lote.id}. "
        f"Stock de producto {db_product.sku} actualizado: "
        f"{stock_anterior} -> {db_product.cantidad_actual}"
    )

    # 7. Refrescar el lote para devolverlo con todos sus datos
    db.refresh(db_lote)
    return db_lote

def register_exit(db: Session, *, exit_in: InventoryExitRequest) -> Movimiento | None:
    """
    Registra una salida de inventario, creando un Movimiento
    y actualizando el stock del Lote y del Producto.
    
    Lanza InsufficientStockError si no hay stock.
    """

    # 1. Obtener el Lote
    logger.info(
        f"Registrando salida de {exit_in.cantidad} "
        f"unidades del lote_id: {exit_in.lote_id}"
    )
    db_lote = get_lote(db, lote_id=exit_in.lote_id)
    if not db_lote:
        logger.warning(f"Lote no encontrado: {exit_in.lote_id}")
        return None # El endpoint lanzara un 404
    
    if db_lote.cantidad_actual < exit_in.cantidad:
        logger.warning(
            f"Stock insuficiente para {db_lote.producto.sku}. "
            f"Solicitado: {exit_in.cantidad}, Disponible: {db_lote.cantidad_actual}"
        )
        raise InsufficientStockError(
            item_sku=db_lote.producto.sku,
            requested=exit_in.cantidad,
            available=db_lote.cantidad_actual
        )
    
    # 2. Obtener el Producto (via la relacion del lote)
    db_product = db_lote.producto
    
    # 3. Crear el Movimiento
    db_movimiento = Movimiento(
        lote_id=db_lote.id,
        tipo="salida",
        cantidad=exit_in.cantidad
    )
    
    # 4. Actualizar el stock
    stock_lote_anterior = db_lote.cantidad_actual
    stock_prod_anterior = db_product.cantidad_actual
    
    db_lote.cantidad_actual -= exit_in.cantidad
    db_product.cantidad_actual -= exit_in.cantidad
    
    # 5. Comitear la transaccion
    db.add(db_movimiento)
    db.add(db_lote)
    db.add(db_product)
    db.commit()
    
    logger.info(
        f"Salida registrada. Lote {db_lote.id} actualizado: "
        f"{stock_lote_anterior} -> {db_lote.cantidad_actual}. "
        f"Producto {db_product.sku} actualizado: "
        f"{stock_prod_anterior} -> {db_product.cantidad_actual}"
    )
    
    db.refresh(db_movimiento)
    return db_movimiento

def smart_dispatch_fefo(
    db: Session, *, dispatch_in: SmartDispatchReq
) -> List[Movimiento]:
    """
    Procesa un despacho inteligente usando la logica FEFO
    (First Expired, First Out).
    """
    cantidad_a_despachar = dispatch_in.cantidad
    logger.info(
        f"Iniciando despacho FEFO de {cantidad_a_despachar} "
        f"unidades para producto_id: {dispatch_in.producto_id}"
    )
    
    # 1. Obtener el producto y su stock total
    db_product = crud_product.get_product(db, product_id=dispatch_in.producto_id)
    if not db_product:
        logger.error(f"Producto no encontrado: {dispatch_in.producto_id}")
        raise ValueError("Producto no encontrado") # Re-lanzar para la API
        
    if db_product.cantidad_actual < cantidad_a_despachar:
        logger.warning(
            f"Stock insuficiente (FEFO) para {db_product.sku}. "
            f"Solicitado: {cantidad_a_despachar}, Disponible: {db_product.cantidad_actual}"
        )
        raise InsufficientStockError(
            item_sku=db_product.sku,
            requested=cantidad_a_despachar,
            available=db_product.cantidad_actual
        )
        
    # 2. Obtener todos los lotes para este producto que tienen stock,
    #    ordenados por fecha de vencimiento (los mas proximos primero).
    lotes_disponibles = (
        db.query(Lote)
        .filter(Lote.producto_id == dispatch_in.producto_id)
        .filter(Lote.cantidad_actual > 0)
        .order_by(Lote.fecha_vencimiento.asc())
        .all()
    )
    
    logger.debug(f"Encontrados {len(lotes_disponibles)} lotes para despachar.")
    
    movimientos_creados = []
    cantidad_despachada_total = 0
    
    # 3. Iterar sobre los lotes y "consumir" el stock
    for lote in lotes_disponibles:
        if cantidad_a_despachar == 0:
            break
            
        cantidad_a_tomar_del_lote = min(lote.cantidad_actual, cantidad_a_despachar)
        
        logger.debug(
            f"Tomando {cantidad_a_tomar_del_lote} de Lote {lote.id} "
            f"(expira: {lote.fecha_vencimiento})"
        )
        
        # 4. Crear el movimiento de salida
        db_movimiento = Movimiento(
            lote_id=lote.id,
            tipo="salida",
            cantidad=cantidad_a_tomar_del_lote
        )
        
        # 5. Actualizar los stocks
        cantidad_a_despachar -= cantidad_a_tomar_del_lote
        cantidad_despachada_total += cantidad_a_tomar_del_lote
        
        lote.cantidad_actual -= cantidad_a_tomar_del_lote
        
        db.add(db_movimiento)
        db.add(lote)
        movimientos_creados.append(db_movimiento)

    # Actualizar el producto una sola vez al final
    stock_prod_anterior = db_product.cantidad_actual
    db_product.cantidad_actual -= cantidad_despachada_total
    db.add(db_product)
    
    db.commit()
    
    logger.info(
        f"Despacho FEFO completado. {cantidad_despachada_total} unidades despachadas. "
        f"Producto {db_product.sku} actualizado: "
        f"{stock_prod_anterior} -> {db_product.cantidad_actual}"
    )
    
    for m in movimientos_creados:
        db.refresh(m)
        
    return movimientos_creados