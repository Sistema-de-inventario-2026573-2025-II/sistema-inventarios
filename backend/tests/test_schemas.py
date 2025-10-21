import pytest
from pydantic import ValidationError

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