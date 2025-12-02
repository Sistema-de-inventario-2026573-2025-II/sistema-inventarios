# sistema-inventarios/backend/app/api/endpoints/inventory.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# Importamos los schemas de Lote de Modulo 1
from app.schemas.lote import LoteCreate, Lote, LoteWithProduct 
from app.schemas.inventory import InventoryExitRequest, SmartDispatchReq
from app.schemas.movimiento import Movimiento
from typing import List
import app.crud.crud_inventory as crud_inventory
from app.api.deps import get_db
from app.core.exceptions import InsufficientStockError

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get(
    "/lotes",
    response_model=List[LoteWithProduct]
)
def read_lotes(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    ) -> List[LoteWithProduct]:
    """
    Obtiene una lista de lotes.
    """

    lotes = crud_inventory.get_lotes(db=db, skip=skip, limit=limit)
    if not lotes:
        raise HTTPException(status_code=404, detail="No hay lotes disponibles")
    return lotes

@router.get(
    "/lotes/{lote_id}",
    response_model=Lote
)
def read_lote_by_id(
    *,
    db: Session = Depends(get_db),
    lote_id: int
) -> Lote:
    """
    Obtiene un lote por su ID.
    """
    lote = crud_inventory.get_lote(db=db, lote_id=lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lote

@router.post(
    "/entradas",
    response_model=Lote,
    status_code=201
)
def register_new_entry(
    *,
    db: Session = Depends(get_db),
    entry_in: LoteCreate  # Usamos el schema LoteCreate como body
) -> Lote:
    """
    Registra una nueva entrada de inventario.
    Crea un Lote y un Movimiento, y actualiza el stock del Producto.
    """
    # Llamamos a nuestra nueva funcion de logica de negocio
    lote = crud_inventory.register_entry(db=db, entry_in=entry_in)
    
    if not lote:
        # Esto ocurre si crud_product.get_product devolvio None
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado. No se pudo registrar la entrada."
        )
    return lote

@router.post(
    "/salidas",
    response_model=Movimiento, # Devuelve el movimiento creado
    status_code=201
)
def register_new_exit(
    *,
    db: Session = Depends(get_db),
    exit_in: InventoryExitRequest
) -> Movimiento:
    """
    Registra una nueva salida de inventario (despacho).
    Crea un Movimiento de 'salida' y actualiza el stock.
    """
    try:
        movimiento = crud_inventory.register_exit(db=db, exit_in=exit_in)
    except InsufficientStockError as e:
        # Atrapar el error y convertirlo en un HTTP 400
        raise HTTPException(
            status_code=400,
            detail=e.message
        )
    
    if not movimiento:
        raise HTTPException(
            status_code=404,
            detail="Lote no encontrado. No se pudo registrar la salida."
        )
    return movimiento

@router.post(
    "/despachar",
    response_model=List[Movimiento], # Devuelve una lista de movimientos
    status_code=200 # 200 OK, ya que es una operacion
)
def smart_dispatch_inventory(
    *,
    db: Session = Depends(get_db),
    dispatch_in: SmartDispatchReq
) -> List[Movimiento]:
    """
    Registra una nueva salida de inventario "inteligente" (FEFO).
    """
    try:
        movimientos = crud_inventory.smart_dispatch_fefo(
            db=db, dispatch_in=dispatch_in
        )
        return movimientos
    except InsufficientStockError as e:
        # Atrapar el error y convertirlo en un HTTP 400
        raise HTTPException(
            status_code=400,
            detail=e.message
        )
    except ValueError as e:
        # Atrapar el error interno que lanzamos desde el CRUD
        logger.error(
            f"Error interno en smart_dispatch_fefo: {e}", 
            exc_info=True  # Esto anadira el traceback al log
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {e}"
        )