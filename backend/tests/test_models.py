# sistema-inventarios/backend/tests/test_models.py
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

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

def test_lote_model_create(db_session: Session):
    """
    Prueba la creacion de una instancia del modelo Lote.
    """
    # Importar el modelo Producto, que sera necesario para la relacion
    from app.models.producto import Producto
    
    # Primero, crear un producto para la llave foranea (foreign key)
    producto = Producto(
        nombre="Producto para Lote",
        sku="SKU-LOTE-TEST",
        precio=10.00
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)

    # Esta importacion fallara
    from app.models.lote import Lote

    lote_nuevo = Lote(
        producto_id=producto.id,
        cantidad_recibida=100,
        fecha_vencimiento=datetime.utcnow().date()
    )
    
    db_session.add(lote_nuevo)
    db_session.commit()
    db_session.refresh(lote_nuevo)
    
    assert lote_nuevo.id is not None
    assert lote_nuevo.producto_id == producto.id
    assert lote_nuevo.cantidad_actual == 100

def test_movimiento_model_create(db_session: Session):
    """
    Prueba la creacion de una instancia del modelo Movimiento.
    """
    # Importar modelos necesarios
    from app.models.producto import Producto
    from app.models.lote import Lote
    
    # Setup: Crear Producto
    producto = Producto(
        nombre="Producto para Movimiento",
        sku="SKU-MOV-TEST",
        precio=10.00
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)

    # Setup: Crear Lote
    lote = Lote(
        producto_id=producto.id,
        cantidad_recibida=100
    )
    db_session.add(lote)
    db_session.commit()
    db_session.refresh(lote)

    # Esta importacion fallara
    from app.models.movimiento import Movimiento

    movimiento_entrada = Movimiento(
        lote_id=lote.id,
        tipo="entrada", # 'entrada' o 'salida' 
        cantidad=100
    )
    
    db_session.add(movimiento_entrada)
    db_session.commit()
    db_session.refresh(movimiento_entrada)
    
    assert movimiento_entrada.id is not None
    assert movimiento_entrada.lote_id == lote.id
    assert movimiento_entrada.tipo == "entrada"
    assert movimiento_entrada.fecha_movimiento is not None # Debe autogenerarse