# sistema-inventarios/backend/app/schemas/movimiento.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal

class MovimientoBase(BaseModel):
    """Esquema base para un movimiento."""
    lote_id: int
    cantidad: int
    tipo: str

class MovimientoCreate(MovimientoBase):
    """Esquema para la creacion de un movimiento."""
    
    # Validacion requerida por el test: tipo debe ser 'entrada' o 'salida'
    tipo: Literal['entrada', 'salida']
    
    # Validacion requerida por el test: cantidad debe ser > 0
    cantidad: int = Field(..., gt=0)

class Movimiento(MovimientoBase):
    """Esquema para leer un movimiento (incluye campos de la BD)."""
    id: int
    fecha_movimiento: datetime

    model_config = ConfigDict(from_attributes=True)