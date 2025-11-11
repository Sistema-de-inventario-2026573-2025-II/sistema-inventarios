# sistema-inventarios/backend/app/crud/crud_product.py
import logging  # <-- 1. Importar
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate
from typing import List

logger = logging.getLogger(__name__)  # <-- 2. Obtener el logger

def create_product(db: Session, *, product_in: ProductoCreate) -> Producto:
    """
    Crea un nuevo producto en la base de datos.
    """
    # Creamos una instancia del modelo SQLAlchemy a partir del schema Pydantic
    logger.info(f"Creando producto con SKU: {product_in.sku}")
    db_product = Producto(
        **product_in.model_dump()
    )
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Producto creado con ID: {db_product.id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear producto con SKU {product_in.sku}: {e}")
        # TODO: Considerar si se debe relanzar el error
        # Por ahora, devolvemos None o dejamos que el error se propague
        raise e

def get_product(db: Session, product_id: int) -> Producto | None:
    """
    Obtiene un producto por su ID.
    """
    logger.debug(f"Buscando producto con id: {product_id}")
    return db.query(Producto).filter(Producto.id == product_id).first()

def get_product_by_sku(db: Session, sku: str) -> Producto | None:
    """
    Obtiene un producto por su SKU.
    """
    logger.debug(f"Buscando producto con sku: {sku}")
    return db.query(Producto).filter(Producto.sku == sku).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Producto]:
    """
    Obtiene una lista de productos con paginacion.
    """
    logger.debug(f"Buscando lista de productos con skip={skip}, limit={limit}")
    return db.query(Producto).offset(skip).limit(limit).all()

def update_product(
    db: Session,
    *,
    db_product: Producto,
    product_in: ProductoUpdate
) -> Producto:
    """
    Actualiza un producto en la base de datos.
    """
    # Cargar los datos del schema Pydantic en un dict
    logger.info(f"Actualizando producto con ID: {db_product.id}")
    update_data = product_in.model_dump(exclude_unset=True)
    
    
    # Iterar sobre los datos y actualizar el modelo SQLAlchemy
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Producto actualizado con ID: {db_product.id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar producto con ID {db_product.id}: {e}")
        raise e

def delete_product(db: Session, *, db_product: Producto) -> Producto:
    """
    Borra un producto de la base de datos.
    """
    product_id = db_product.id
    logger.info(f"Borrando producto con ID: {product_id}")
    try:
        db.delete(db_product)
        db.commit()
        logger.info(f"Producto borrado con ID: {product_id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error al borrar producto con ID {product_id}: {e}")
        raise e