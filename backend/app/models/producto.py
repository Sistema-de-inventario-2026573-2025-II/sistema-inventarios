# sistema-inventarios/backend/app/models/producto.py
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    precio = Column(Float, nullable=False)
    cantidad_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)

    __table_args__ = (UniqueConstraint('sku', name='uq_sku'),)