# sistema-inventarios/backend/app/models/movimiento.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Llave foranea al lote
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    
    tipo = Column(String, nullable=False) # 'entrada' o 'salida'
    cantidad = Column(Integer, nullable=False)
    
    # Se autogenera al crear
    fecha_movimiento = Column(DateTime(timezone=True), server_default=func.now())

    # Relacion con el lote (para ORM)
    lote = relationship("Lote")

    def __init__(self, *args, **kwargs):
        """
        Sobrescribe el init para manejar la fecha_movimiento 
        si no se provee un default del servidor (util para pruebas).
        """
        super().__init__(*args, **kwargs)
        if self.fecha_movimiento is None:
            self.fecha_movimiento = datetime.now(timezone.utc)