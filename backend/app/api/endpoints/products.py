# sistema-inventarios/backend/app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.schemas.producto as product_schema
import app.crud.crud_product as crud_product
from app.api.deps import get_db

router = APIRouter()

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