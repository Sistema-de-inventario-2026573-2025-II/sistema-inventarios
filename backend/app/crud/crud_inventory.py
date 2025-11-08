# sistema-inventarios/backend/app/crud/crud_inventory.py
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.models.lote import Lote
from app.models.movimiento import Movimiento
from app.schemas.lote import LoteCreate
from app.schemas.inventory import InventoryExitRequest, SmartDispatchReq
import app.crud.crud_product as crud_product
from app.core.exceptions import InsufficientStockError
from typing import List

def get_lote(db: Session, lote_id: int) -> Lote | None:
    """
    Obtiene un lote por su ID.
    """
    return db.query(Lote).filter(Lote.id == lote_id).first()

def register_entry(db: Session, *, entry_in: LoteCreate) -> Lote | None:
    """
    Registra una entrada de inventario, creando un Lote, un Movimiento
    y actualizando el stock del Producto.
    """
    # 1. Obtener el producto (usamos el CRUD de producto existente)
    db_product = crud_product.get_product(db, product_id=entry_in.producto_id)
    if not db_product:
        return None # El endpoint lanzara un 404

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

    # 4. Crear el Movimiento
    db_movimiento = Movimiento(
        lote_id=db_lote.id,
        tipo="entrada",
        cantidad=entry_in.cantidad_recibida
    )
    
    # 5. Actualizar el stock del Producto
    db_product.cantidad_actual += entry_in.cantidad_recibida
    
    # 6. Añadir los objetos restantes a la sesion y comitear la transaccion
    db.add(db_movimiento)
    db.add(db_product)
    db.commit()
    
    # 7. Refrescar el lote para devolverlo con todos sus datos
    db.refresh(db_lote)
    return db_lote

def register_exit(db: Session, *, exit_in: InventoryExitRequest) -> Movimiento | None:
    """
    Registra una salida de inventario, creando un Movimiento
    y actualizando el stock del Lote y del Producto.
    """
   # 1. Obtener el Lote (Usamos nuestra nueva funcion)
    db_lote = get_lote(db, lote_id=exit_in.lote_id)
    if not db_lote:
        return None # El endpoint lanzara un 404
    
    if db_lote.cantidad_actual < exit_in.cantidad:
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
    db_lote.cantidad_actual -= exit_in.cantidad
    db_product.cantidad_actual -= exit_in.cantidad
    
    # 5. Comitear la transaccion
    db.add(db_movimiento)
    db.add(db_lote)
    db.add(db_product)
    db.commit()
    
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
    
    # 1. Obtener el producto y su stock total
    db_product = crud_product.get_product(db, product_id=dispatch_in.producto_id)
    if not db_product:
        # Esto no deberia pasar si la BD esta bien, pero por si acaso.
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    if db_product.cantidad_actual < cantidad_a_despachar:
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
    
    movimientos_creados = []
    
    # 3. Iterar sobre los lotes y "consumir" el stock
    for lote in lotes_disponibles:
        if cantidad_a_despachar == 0:
            break # Ya hemos despachado todo
            
        cantidad_a_tomar_del_lote = min(lote.cantidad_actual, cantidad_a_despachar)
        
        # 4. Crear el movimiento de salida
        db_movimiento = Movimiento(
            lote_id=lote.id,
            tipo="salida",
            cantidad=cantidad_a_tomar_del_lote
        )
        
        # 5. Actualizar los stocks
        cantidad_a_despachar -= cantidad_a_tomar_del_lote
        lote.cantidad_actual -= cantidad_a_tomar_del_lote
        db_product.cantidad_actual -= cantidad_a_tomar_del_lote
        
        db.add(db_movimiento)
        db.add(lote)
        movimientos_creados.append(db_movimiento)

    # 6. Comitear toda la transaccion
    db.add(db_product)
    db.commit()
    
    # Refrescar los movimientos para que tengan sus IDs
    for m in movimientos_creados:
        db.refresh(m)
        
    return movimientos_creados