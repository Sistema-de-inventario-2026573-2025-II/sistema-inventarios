import pytest
from pydantic import ValidationError
from datetime import date, timedelta, datetime

def test_producto_schema_import():
    """
    Prueba que los esquemas de Pydantic para Producto se pueden importar.
    """
    # Esta importacion fallara
    from app.schemas.producto import Producto, ProductoCreate, ProductoBase
    
    assert Producto is not None
    assert ProductoCreate is not None
    assert ProductoBase is not None

def test_producto_create_schema_validation():
    """
    Prueba que el esquema ProductoCreate valida correctamente los datos.
    """
    from app.schemas.producto import ProductoCreate
    
    # Datos validos
    data = {
        "nombre": "Producto Valido",
        "sku": "SKU123",
        "precio": 10.50,
        "stock_minimo": 5
    }
    schema = ProductoCreate(**data)
    assert schema.nombre == "Producto Valido"
    assert schema.precio == 10.50
    
    # Datos invalidos (precio negativo)
    with pytest.raises(ValidationError):
        ProductoCreate(
            nombre="Producto Invalido",
            sku="SKU456",
            precio=-1.00 # El precio no debe ser negativo
        )

def test_lote_schema_import():
    """Prueba que los esquemas de Pydantic para Lote se pueden importar."""
    # Esta importacion fallara
    from app.schemas.lote import Lote, LoteCreate, LoteBase
    
    assert Lote is not None
    assert LoteCreate is not None
    assert LoteBase is not None

def test_lote_create_schema_validation():
    """
    Prueba que LoteCreate valida que la cantidad_recibida es positiva.
    """
    from app.schemas.lote import LoteCreate
    
    # Datos validos
    valid_data = {
        "producto_id": 1,
        "cantidad_recibida": 100,
        "fecha_vencimiento": date.today() + timedelta(days=30)
    }
    schema = LoteCreate(**valid_data)
    assert schema.cantidad_recibida == 100
    
    # Datos invalidos (cantidad_recibida debe ser > 0)
    invalid_data = valid_data.copy()
    invalid_data["cantidad_recibida"] = 0 # No debe ser 0

    with pytest.raises(ValidationError):
        LoteCreate(**invalid_data)
    
    invalid_data["cantidad_recibida"] = -50 # No debe ser negativa
    with pytest.raises(ValidationError):
        LoteCreate(**invalid_data)

def test_movimiento_schema_import():
    """Prueba que los esquemas de Pydantic para Movimiento se pueden importar."""
    # Esta importacion fallara
    from app.schemas.movimiento import Movimiento, MovimientoCreate, MovimientoBase
    
    assert Movimiento is not None
    assert MovimientoCreate is not None
    assert MovimientoBase is not None

def test_movimiento_create_schema_validation():
    """
    Prueba que MovimientoCreate valida los datos correctamente.
    """
    from app.schemas.movimiento import MovimientoCreate
    
    # Datos validos
    valid_data = {
        "lote_id": 1,
        "tipo": "entrada",
        "cantidad": 100
    }
    schema = MovimientoCreate(**valid_data)
    assert schema.cantidad == 100
    assert schema.tipo == "entrada"
    
    # Datos invalidos (tipo debe ser 'entrada' o 'salida')
    invalid_data = valid_data.copy()
    invalid_data["tipo"] = "transferencia" # Tipo no valido

    with pytest.raises(ValidationError):
        MovimientoCreate(**invalid_data)

    # Datos invalidos (cantidad debe ser > 0)
    invalid_data = valid_data.copy()
    invalid_data["cantidad"] = 0 # Cantidad no valida

    with pytest.raises(ValidationError):
        MovimientoCreate(**invalid_data)