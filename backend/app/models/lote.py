from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Llave foranea al producto
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    cantidad_recibida = Column(Integer, nullable=False)
    # cantidad_actual se inicializa con cantidad_recibida
    cantidad_actual = Column(Integer, nullable=False)
    
    fecha_vencimiento = Column(Date)

    # Relacion con el producto (para ORM)
    producto = relationship("Producto")

    def __init__(self, *args, **kwargs):
        """
        Sobrescribe el init para asegurar que cantidad_actual
        se establece igual a cantidad_recibida al crear.
        """
        super().__init__(*args, **kwargs)
        self.cantidad_actual = self.cantidad_recibida