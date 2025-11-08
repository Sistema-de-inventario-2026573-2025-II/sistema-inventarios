# sistema-inventarios/backend/app/crud/crud_product.py
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate
from typing import List

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

def get_product(db: Session, product_id: int) -> Producto | None:
    """
    Obtiene un producto por su ID.
    """
    return db.query(Producto).filter(Producto.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Producto]:
    """
    Obtiene una lista de productos con paginacion.
    """
    return db.query(Producto).offset(skip).limit(limit).all()

def update_product(
    db: Session,
    *,
    db_product: Producto, # El producto que ya existe
    product_in: ProductoUpdate # Los datos para actualizar
) -> Producto:
    """
    Actualiza un producto en la base de datos.
    """
    # Cargar los datos del schema Pydantic en un dict
    update_data = product_in.model_dump(exclude_unset=True)
    
    # Iterar sobre los datos y actualizar el modelo SQLAlchemy
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, *, db_product: Producto) -> Producto:
    """
    Borra un producto de la base de datos.
    """
    db.delete(db_product)
    db.commit()
    # El objeto 'db_product' todavia tiene sus datos
    # y puede ser devuelto (como espera nuestra prueba).
    return db_product