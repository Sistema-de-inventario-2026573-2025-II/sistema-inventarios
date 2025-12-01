# sistema-inventarios/backend/app/schemas/alerta.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class AlertaBase(BaseModel):
    tipo_alerta: str
    entidad_id: int
    entidad_tipo: str
    mensaje: str
    esta_activa: bool = True
    metadata_json: Optional[Dict[str, Any]] = None

class AlertaCreate(AlertaBase):
    pass

class AlertaUpdate(AlertaBase):
    pass

class AlertaInDB(AlertaBase):
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)