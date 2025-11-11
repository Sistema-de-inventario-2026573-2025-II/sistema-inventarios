# sistema-inventarios/backend/app/api/endpoints/products.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.schemas.producto as product_schema
import app.crud.crud_product as crud_product
from app.api.deps import get_db, get_product_or_404
from app.models.producto import Producto
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=List[product_schema.Producto] # El response es una Lista
)
def read_all_products(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[product_schema.Producto]:
    """
    Obtiene una lista de todos los productos.
    """
    logger.debug(f"Buscando lista de productos con skip={skip}, limit={limit}")
    products = crud_product.get_products(db=db, skip=skip, limit=limit)
    return products


@router.post(
    "/",
    response_model=product_schema.Producto,
    status_code=201
)
def create_new_product(
    *,
    db: Session = Depends(get_db),
    product_in: product_schema.ProductoCreate
) -> product_schema.Producto:
    """
    Crea un nuevo producto en el sistema.
    """
    # 1. Chequeo proactivo de SKU (esto arregla el test)
    logger.debug(f"Verificando si SKU {product_in.sku} ya existe")
    db_product = crud_product.get_product_by_sku(db=db, sku=product_in.sku)
    if db_product:
        logger.warning(
            f"SKU duplicado. Se intento crear {product_in.sku}, "
            f"pero ya existe con id {db_product.id}"
        )
        raise HTTPException(
            status_code=409,  # 409 Conflict!
            detail=f"Un producto con este SKU '{product_in.sku}' ya existe."
        )
    
    # 2. Refactor del try/except
    try:
        logger.info(f"Recibida solicitud para crear producto SKU: {product_in.sku}")
        product = crud_product.create_product(db=db, product_in=product_in)
        return product
    except IntegrityError as e:  # <-- Ser mas especifico
        # Esto es para otros errores (ej: 'nombre' es null)
        db.rollback()
        logger.error(
            f"Error de integridad al crear producto SKU {product_in.sku}: {e}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error de base de datos: {e}"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error inesperado al crear producto SKU {product_in.sku}: {e}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {e}"
        )


@router.get(
    "/{product_id}",
    response_model=product_schema.Producto
)
def read_product_by_id(
    *,
    db_product: Producto = Depends(get_product_or_404)
) -> product_schema.Producto:
    """
    Obtiene un producto por su ID.
    """
    return db_product

@router.put(
    "/{product_id}",
    response_model=product_schema.Producto
)
def update_existing_product(
    *,
    db: Session = Depends(get_db),
    db_product: Producto = Depends(get_product_or_404),
    product_in: product_schema.ProductoUpdate
) -> product_schema.Producto:
    """
    Actualiza un producto existente por su ID.
    """
    try:
        logger.info(f"Actualizando producto con id: {db_product.id}")
        product = crud_product.update_product(
            db=db, db_product=db_product, product_in=product_in
        )
        return product
    except Exception as e:
        logger.error(
            f"Error al actualizar producto con id {db_product.id}: {e}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo actualizar el producto: {e}"
        )

@router.delete(
    "/{product_id}",
    response_model=product_schema.Producto
)
def delete_existing_product(
    *,
    db: Session = Depends(get_db),
    db_product: Producto = Depends(get_product_or_404),
) -> product_schema.Producto:
    """
    Borra un producto existente por su ID.
    """
    try:
        logger.info(f"Borrando producto con id: {db_product.id}")
        product = crud_product.delete_product(db=db, db_product=db_product)
        return product
    except Exception as e:
        logger.error(
            f"Error al borrar producto con id {db_product.id}: {e}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo borrar el producto: {e}"
        )