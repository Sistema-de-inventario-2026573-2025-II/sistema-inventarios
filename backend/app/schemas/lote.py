# sistema-inventarios/backend/app/schemas/lote.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

class LoteBase(BaseModel):
    """Esquema base para un lote."""
    producto_id: int
    cantidad_recibida: int
    fecha_vencimiento: Optional[date] = None

class LoteCreate(LoteBase):
    """Esquema para la creacion de un lote."""
    # Esto es lo que el test esta validando
    cantidad_recibida: int = Field(..., gt=0) # gt=0 means "greater than 0"

class Lote(LoteBase):
    """Esquema para leer un lote (incluye campos de la BD)."""
    id: int
    cantidad_actual: int

    model_config = ConfigDict(from_attributes=True)