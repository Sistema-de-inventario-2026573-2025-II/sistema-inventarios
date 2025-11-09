# sistema-inventarios/backend/app/services/alerts.py
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.producto import Producto
from app.models.lote import Lote
from typing import List
from datetime import date, timedelta

def check_stock_minimo(db: Session) -> List[Producto]:
    """
    Servicio que devuelve una lista de todos los productos
    que estan por debajo de su stock minimo.
    """
    # Usamos un query de SQLAlchemy.
    # Compara la columna 'cantidad_actual' con la columna 'stock_minimo'
    stmt = select(Producto).where(Producto.cantidad_actual < Producto.stock_minimo)
    
    productos_en_alerta = db.scalars(stmt).all()
    
    return list(productos_en_alerta)

def check_lotes_por_vencer(db: Session, *, days_threshold: int = 30) -> List[Lote]:
    """
    Servicio que devuelve una lista de lotes que estan por vencer
    dentro del umbral de dias especificado (days_threshold).
    """
    # 1. Calcular la fecha limite
    today = date.today()
    target_date = today + timedelta(days=days_threshold)
    
    # 2. Construir el query
    stmt = select(Lote).where(
        and_(
            Lote.fecha_vencimiento.isnot(None),  
            Lote.cantidad_actual > 0,          
            Lote.fecha_vencimiento > today,    
            Lote.fecha_vencimiento <= target_date 
        )
    ).order_by(Lote.fecha_vencimiento.asc()) 
    
    # 3. Ejecutar y devolver
    lotes_en_alerta = db.scalars(stmt).all()
    
    return list(lotes_en_alerta)