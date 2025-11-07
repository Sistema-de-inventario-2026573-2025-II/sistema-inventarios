# sistema-inventarios/backend/app/crud/crud_product.py
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate

def create_product(db: Session, *, product_in: ProductoCreate) -> Producto:
    """
    Crea un nuevo producto en la base de datos.
    """
    # Creamos una instancia del modelo SQLAlchemy a partir del schema Pydantic
    db_product = Producto(
        **product_in.model_dump()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product