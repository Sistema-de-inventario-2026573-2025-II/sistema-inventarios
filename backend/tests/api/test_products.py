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

def test_get_all_products(test_client: TestClient):
    """
    Prueba para GET /api/v1/productos (listar todos).
    Primero crea dos productos y luego prueba que la lista los devuelve.
    """
    # ETAPA 1: SETUP - Crear dos productos
    product_data_1 = {
        "nombre": "List Producto 1",
        "sku": "SKU-LIST-001",
        "precio": 10.00
    }
    product_data_2 = {
        "nombre": "List Producto 2",
        "sku": "SKU-LIST-002",
        "precio": 20.00
    }
    response_create_1 = test_client.post("/api/v1/productos", json=product_data_1)
    response_create_2 = test_client.post("/api/v1/productos", json=product_data_2)
    assert response_create_1.status_code == 201
    assert response_create_2.status_code == 201

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    response_get = test_client.get("/api/v1/productos")

    # Esperamos 200 OK, pero obtendremos 405 Method Not Allowed
    assert response_get.status_code == 200
    
    # Verificamos que los datos sean correctos
    data = response_get.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["sku"] == "SKU-LIST-001"
    assert data[1]["sku"] == "SKU-LIST-002"

def test_update_product(test_client: TestClient):
    """
    Prueba para PUT /api/v1/productos/{id}.
    Primero crea un producto, luego prueba que se puede actualizar.
    """
    # ETAPA 1: SETUP - Crear un producto
    product_data = {
        "nombre": "Producto Original",
        "sku": "SKU-UPDATE-001",
        "precio": 100.00
    }
    response_create = test_client.post("/api/v1/productos", json=product_data)
    assert response_create.status_code == 201
    created_product = response_create.json()
    product_id = created_product["id"]

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    update_data = {
        "nombre": "Producto Actualizado",
        "sku": "SKU-UPDATE-001", # SKU no cambia
        "precio": 150.50,
        "stock_minimo": 20
    }
    response_update = test_client.put(
        f"/api/v1/productos/{product_id}",
        json=update_data
    )

    # Esperamos 200 OK, pero obtendremos 405 Method Not Allowed
    assert response_update.status_code == 200
    
    # Verificamos que los datos se hayan actualizado
    data = response_update.json()
    assert data["nombre"] == "Producto Actualizado"
    assert data["precio"] == 150.50
    assert data["stock_minimo"] == 20
    assert data["id"] == product_id

def test_delete_product(test_client: TestClient):
    """
    Prueba para DELETE /api/v1/productos/{id}.
    Primero crea un producto, prueba que se puede borrar,
    y luego prueba que no se puede obtener (GET).
    """
    # ETAPA 1: SETUP - Crear un producto
    product_data = {
        "nombre": "Producto a Borrar",
        "sku": "SKU-DELETE-001",
        "precio": 10.00
    }
    response_create = test_client.post("/api/v1/productos", json=product_data)
    assert response_create.status_code == 201
    created_product = response_create.json()
    product_id = created_product["id"]

    # ETAPA 2: LA PRUEBA DE BORRADO (Esto es lo que fallara)
    response_delete = test_client.delete(f"/api/v1/productos/{product_id}")

    # Esperamos 200 OK, pero obtendremos 405 Method Not Allowed
    assert response_delete.status_code == 200
    
    # Verificamos que devolvio el producto borrado
    data = response_delete.json()
    assert data["id"] == product_id
    assert data["sku"] == "SKU-DELETE-001"

    # ETAPA 3: VERIFICACION
    # Probamos que el producto ya no existe
    response_get = test_client.get(f"/api/v1/productos/{product_id}")
    assert response_get.status_code == 404