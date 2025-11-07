# sistema-inventarios/backend/app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.schemas.producto as product_schema
import app.crud.crud_product as crud_product
from app.api.deps import get_db
from typing import List

router = APIRouter()


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
    products = crud_product.get_products(db=db, skip=skip, limit=limit)
    return products


@router.post(
    "/",
    response_model=product_schema.Producto,
    status_code=201  # HTTP 201 Created
)
def create_new_product(
    *,
    db: Session = Depends(get_db),
    product_in: product_schema.ProductoCreate
) -> product_schema.Producto:
    """
    Crea un nuevo producto en el sistema.
    """
    # Llama a la funcion CRUD para crear el producto
    product = crud_product.create_product(db=db, product_in=product_in)
    return product


@router.get(
    "/{product_id}",
    response_model=product_schema.Producto
)
def read_product_by_id(
    *,
    db: Session = Depends(get_db),
    product_id: int
) -> product_schema.Producto:
    """
    Obtiene un producto por su ID.
    """
    product = crud_product.get_product(db=db, product_id=product_id)
    if not product:
        # Esto es importante para un manejo de errores robusto
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.put(
    "/{product_id}",
    response_model=product_schema.Producto
)
def update_existing_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: product_schema.ProductoUpdate # Usamos el nuevo schema
) -> product_schema.Producto:
    """
    Actualiza un producto existente por su ID.
    """
    # 1. Buscar el producto
    db_product = crud_product.get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # 2. Llamar al CRUD para actualizarlo
    product = crud_product.update_product(
        db=db, db_product=db_product, product_in=product_in
    )
    return product

@router.delete(
    "/{product_id}",
    response_model=product_schema.Producto
)
def delete_existing_product(
    *,
    db: Session = Depends(get_db),
    product_id: int
) -> product_schema.Producto:
    """
    Borra un producto existente por su ID.
    """
    # 1. Buscar el producto
    db_product = crud_product.get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # 2. Llamar al CRUD para borrarlo
    product = crud_product.delete_product(db=db, db_product=db_product)
    return product