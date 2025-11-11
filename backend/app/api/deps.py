# sistema-inventarios/backend/app/api/deps.py
import logging
from collections.abc import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from app.db.session import SessionLocal
import app.crud.crud_product as crud_product  
from app.models.producto import Producto  

logger = logging.getLogger(__name__)

def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para obtener una sesion de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_product_or_404(
    product_id: int = Path(..., title="El ID del producto a buscar"),
    db: Session = Depends(get_db)
) -> Producto:
    """
    Dependencia que obtiene un producto por ID o lanza un 404.
    """
    logger.debug(f"Buscando producto con id: {product_id}")
    db_product = crud_product.get_product(db=db, product_id=product_id)
    if not db_product:
        logger.warning(f"Producto no encontrado con id: {product_id}")
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    return db_product