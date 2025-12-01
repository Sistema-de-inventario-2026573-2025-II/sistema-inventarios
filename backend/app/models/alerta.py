# sistema-inventarios/backend/app/models/alerta.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from app.db.base import Base
from datetime import datetime

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    tipo_alerta = Column(String, index=True, nullable=False) # e.g., "stock_minimo", "por_vencer"
    entidad_id = Column(Integer, nullable=False) # ID de la entidad (Producto o Lote) que genero la alerta
    entidad_tipo = Column(String, nullable=False) # "producto" o "lote"
    mensaje = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    esta_activa = Column(Boolean, default=True, nullable=False)
    # metadata_json puede contener detalles como nombre de producto, SKU, fecha de vencimiento, etc.
    metadata_json = Column(JSON, nullable=True) 