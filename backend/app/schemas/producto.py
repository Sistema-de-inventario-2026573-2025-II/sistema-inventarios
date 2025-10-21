# sistema-inventarios/backend/app/schemas/producto.py
from pydantic import BaseModel, Field, ConfigDict

class ProductoBase(BaseModel):
    """Esquema base para un producto."""
    nombre: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    precio: float
    stock_minimo: int = Field(default=5)

class ProductoCreate(ProductoBase):
    """Esquema para la creacion de un producto."""
    precio: float = Field(..., gt=0) # gt=0 means "greater than 0"

class Producto(ProductoBase):
    """
    Esquema para leer un producto (incluye campos de la BD como el id).
    """
    id: int
    cantidad_actual: int

    model_config = ConfigDict(from_attributes=True)