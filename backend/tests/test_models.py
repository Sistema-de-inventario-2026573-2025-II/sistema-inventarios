# sistema-inventarios/backend/tests/test_models.py
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
# --- Importar los modelos que vamos a probar ---
from app.models.producto import Producto
from app.models.lote import Lote
from app.models.movimiento import Movimiento

def test_producto_model_create(product_model_in_db: Producto):
    """Prueba que el fixture del modelo Producto funciona."""
    assert product_model_in_db.id is not None
    assert product_model_in_db.sku == "SKU-MODEL-001"

def test_producto_model_sku_unique(db_session: Session, product_model_in_db: Producto):
    """
    Prueba que la restriccion 'unique' en el SKU funciona.
    Usa el fixture para el primer producto.
    """
    
    producto2 = Producto(
        nombre="Producto 2",
        sku="SKU-MODEL-001",  # Mismo SKU
        precio=20.00,
        cantidad_actual=20,
        stock_minimo=5
    )
    
    db_session.add(producto2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_lote_model_create(lote_model_in_db: Lote, product_model_in_db: Producto):
    """
    Prueba que el fixture del modelo Lote funciona.
    """
    assert lote_model_in_db.id is not None
    assert lote_model_in_db.producto_id == product_model_in_db.id
    assert lote_model_in_db.cantidad_actual == 50 # Se inicializo correctamente


def test_movimiento_model_create(db_session: Session, lote_model_in_db: Lote):
    """
    Prueba la creacion de una instancia del modelo Movimiento.
    Usa el fixture de Lote (que a su vez usa el de Producto).
    """
    movimiento_entrada = Movimiento(
        lote_id=lote_model_in_db.id,
        tipo="entrada",
        cantidad=50 # Coincide con la cantidad del lote del fixture
    )
    
    db_session.add(movimiento_entrada)
    db_session.commit()
    db_session.refresh(movimiento_entrada)
    
    assert movimiento_entrada.id is not None
    assert movimiento_entrada.lote_id == lote_model_in_db.id
    assert movimiento_entrada.tipo == "entrada"
    assert movimiento_entrada.fecha_movimiento is not None