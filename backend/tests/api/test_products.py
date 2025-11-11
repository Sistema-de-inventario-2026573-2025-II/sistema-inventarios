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

def test_get_product_by_id(test_client: TestClient, product_in_db: dict):
    """
    Prueba para GET /api/v1/productos/{id}.
    Primero crea un producto y luego prueba que se puede obtener.
    """
    # ETAPA 1: SETUP - Hecho por el fixture!
    product_id = product_in_db["id"]
    product_sku = product_in_db["sku"]

    # ETAPA 2: LA PRUEBA
    response_get = test_client.get(f"/api/v1/productos/{product_id}")

    assert response_get.status_code == 200
    data = response_get.json()
    assert data["id"] == product_id
    assert data["sku"] == product_sku

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

def test_update_product(test_client: TestClient, product_in_db: dict):
    """
    Prueba para PUT /api/v1/productos/{id}.
    Usa el fixture 'product_in_db' para el setup.
    """
    # ETAPA 1: SETUP - Hecho por el fixture!
    product_id = product_in_db["id"]

    # ETAPA 2: LA PRUEBA
    update_data = {
        "nombre": "Producto Actualizado",
        "sku": product_in_db["sku"], # Usar el mismo SKU
        "precio": 150.50,
        "stock_minimo": 20
    }
    response_update = test_client.put(
        f"/api/v1/productos/{product_id}",
        json=update_data
    )

    assert response_update.status_code == 200
    data = response_update.json()
    assert data["nombre"] == "Producto Actualizado"
    assert data["precio"] == 150.50
    assert data["id"] == product_id

def test_delete_product(test_client: TestClient, product_in_db: dict):
    """
    Prueba para DELETE /api/v1/productos/{id}.
    Usa el fixture 'product_in_db' para el setup.
    """
    # ETAPA 1: SETUP - Hecho por el fixture!
    product_id = product_in_db["id"]
    product_sku = product_in_db["sku"]

    # ETAPA 2: LA PRUEBA DE BORRADO
    response_delete = test_client.delete(f"/api/v1/productos/{product_id}")

    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data["id"] == product_id
    assert data["sku"] == product_sku

    # ETAPA 3: VERIFICACION
    response_get = test_client.get(f"/api/v1/productos/{product_id}")
    assert response_get.status_code == 404

    # ETAPA 3: VERIFICACION
    # Probamos que el producto ya no existe
    response_get = test_client.get(f"/api/v1/productos/{product_id}")
    assert response_get.status_code == 404

def test_create_product_duplicate_sku(
    test_client: TestClient, 
    product_in_db: dict
):
    """
    Prueba que la API previene la creacion de un producto
    con un SKU duplicado y devuelve 409 Conflict.
    """
    
    product_data = {
        "nombre": "Producto Duplicado",
        "sku": "SKU-FIXTURE-001",
        "precio": 1.00,
        "stock_minimo": 1
    }
    
    response = test_client.post("/api/v1/productos", json=product_data)
    
    assert response.status_code == 409
    
    data = response.json()
    assert "detail" in data
    assert "SKU" in data["detail"]
    assert "ya existe" in data["detail"]