# sistema-inventarios/backend/app/schemas/inventory.py
from pydantic import BaseModel, Field

class InventoryExitRequest(BaseModel):
    """
    Esquema para una solicitud de salida de inventario.
    """
    lote_id: int
    cantidad: int = Field(..., gt=0) # La cantidad debe ser positiva


class SmartDispatchReq(BaseModel):
    """
    Esquema para una solicitud de despacho "inteligente" (por producto_id).
    """
    producto_id: int
    cantidad: int = Field(..., gt=0) # La cantidad debe ser positiva