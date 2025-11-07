# sistema-inventarios/backend/tests/api/test_products.py
from fastapi.testclient import TestClient

def test_create_product(test_client: TestClient): 
    """
    Prueba para POST /api/v1/productos (Tarea 2.1).
    """
    product_data = {
        "nombre": "Test Producto API",
        "sku": "SKU-API-001",
        "precio": 99.99,
        "stock_minimo": 10
    }
    
    response = test_client.post("/api/v1/productos", json=product_data)
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["sku"] == "SKU-API-001"
    assert data["nombre"] == "Test Producto API"
    assert "id" in data
    assert data["cantidad_actual"] == 0

def test_get_product_by_id(test_client: TestClient):
    """
    Prueba para GET /api/v1/productos/{id}.
    Primero crea un producto y luego prueba que se puede obtener.
    """
    # ETAPA 1: SETUP - Crear un producto para poder obtenerlo
    product_data = {
        "nombre": "Producto para GET",
        "sku": "SKU-GET-001",
        "precio": 50.00,
        "stock_minimo": 1
    }
    response_create = test_client.post("/api/v1/productos", json=product_data)
    assert response_create.status_code == 201
    created_data = response_create.json()
    product_id = created_data["id"]

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    response_get = test_client.get(f"/api/v1/productos/{product_id}")

    # Esperamos 200 OK, pero obtendremos 404 Not Found
    assert response_get.status_code == 200
    
    # Verificamos que los datos sean correctos
    data = response_get.json()
    assert data["id"] == product_id
    assert data["sku"] == "SKU-GET-001"