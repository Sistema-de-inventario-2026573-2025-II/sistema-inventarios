# sistema-inventarios/backend/tests/test_models.py
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

def test_producto_model_create(db_session: Session):
    """
    Prueba la creacion de una instancia del modelo Producto y
    la persistencia en la base de datos.
    """
    from app.models.producto import Producto

    producto_nuevo = Producto(
        nombre="Test Producto",
        sku="SKU12345",
        precio=19.99,
        cantidad_actual=100,
        stock_minimo=10
    )
    
    db_session.add(producto_nuevo)
    db_session.commit()
    db_session.refresh(producto_nuevo)
    
    assert producto_nuevo.id is not None
    assert producto_nuevo.sku == "SKU12345"

def test_producto_model_sku_unique(db_session: Session):
    """
    Prueba que la restriccion 'unique' en el SKU funciona.
    """
    from app.models.producto import Producto

    producto1 = Producto(
        nombre="Producto 1",
        sku="SKU_UNIQUE",
        precio=10.00,
        cantidad_actual=10,
        stock_minimo=5
    )
    db_session.add(producto1)
    db_session.commit()

    producto2 = Producto(
        nombre="Producto 2",
        sku="SKU_UNIQUE",  # Mismo SKU
        precio=20.00,
        cantidad_actual=20,
        stock_minimo=5
    )
    
    db_session.add(producto2)
    # Esperamos que esto falle
    with pytest.raises(IntegrityError):
        db_session.commit()