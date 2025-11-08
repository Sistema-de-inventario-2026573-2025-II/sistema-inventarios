# sistema-inventarios/backend/tests/api/test_inventory.py
from fastapi.testclient import TestClient
from datetime import date, timedelta

def test_register_inventory_entry(test_client: TestClient, product_in_db: dict):
    """
    Prueba para POST /api/v1/entradas (Task 3.1).
    Esto debe crear un Lote y un Movimiento.
    """
    product_id = product_in_db["id"]
    
    entry_data = {
        "producto_id": product_id,
        "cantidad_recibida": 100,
        "fecha_vencimiento": (date.today() + timedelta(days=30)).isoformat()
    }
    
    # ETAPA 1: LA PRUEBA (Esto es lo que fallara)
    response = test_client.post("/api/v1/inventario/entradas", json=entry_data)
    
    # Esperamos 201 Created, pero obtendremos 404 Not Found
    assert response.status_code == 201
    
    # Verificamos la respuesta (debe devolver el Lote creado)
    data = response.json()
    assert "id" in data
    assert data["producto_id"] == product_id
    assert data["cantidad_recibida"] == 100
    assert data["cantidad_actual"] == 100 # El Lote debe estar lleno
    
    # ETAPA 2: VERIFICACION
    # Verificamos que la cantidad del *Producto* se haya actualizado
    product_response = test_client.get(f"/api/v1/productos/{product_id}")
    assert product_response.status_code == 200
    product_data = product_response.json()
    assert product_data["cantidad_actual"] == 100
    
def test_register_inventory_exit(test_client: TestClient, product_in_db: dict):
    """
    Prueba para POST /api/v1/inventario/salidas (Task 3.4).
    Esto debe crear un Movimiento de 'salida' y actualizar el stock
    del Lote y del Producto.
    """
    product_id = product_in_db["id"]
    
    # ETAPA 1: SETUP - Registrar una ENTRADA de 100 unidades
    entry_data = {
        "producto_id": product_id,
        "cantidad_recibida": 100,
        "fecha_vencimiento": (date.today() + timedelta(days=30)).isoformat()
    }
    entry_response = test_client.post("/api/v1/inventario/entradas", json=entry_data)
    assert entry_response.status_code == 201
    lote_data = entry_response.json()
    lote_id = lote_data["id"]

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    # Queremos registrar una SALIDA de 30 unidades
    exit_data = {
        "lote_id": lote_id,
        "cantidad": 30
    }
    
    response = test_client.post("/api/v1/inventario/salidas", json=exit_data)
    
    # Esperamos 201 Created, pero obtendremos 404 Not Found
    assert response.status_code == 201
    
    # Verificamos la respuesta (debe devolver el Movimiento creado)
    data = response.json()
    assert "id" in data
    assert data["tipo"] == "salida"
    assert data["lote_id"] == lote_id
    assert data["cantidad"] == 30
    
    # ETAPA 3: VERIFICACION
    # 3.1: El Producto debe tener 100 - 30 = 70 unidades
    product_response = test_client.get(f"/api/v1/productos/{product_id}")
    product_data = product_response.json()
    assert product_data["cantidad_actual"] == 70
    
    # 3.2: TODO: Verificar que el Lote tiene 70 unidades
    # TODO: (Task 3.x): Implementar un endpoint GET /api/v1/lotes/{lote_id}
    # TODO: y anadir una asercion aqui para verificar que
    # lote_data["cantidad_actual"] == 70.

def test_register_inventory_exit_insufficient_stock(
    test_client: TestClient, 
    product_in_db: dict
):
    """
    Prueba que la API previene una salida si no hay stock suficiente.
    (Task 3.7)
    """
    product_id = product_in_db["id"]
    
    # ETAPA 1: SETUP - Registrar una ENTRADA de 100 unidades
    entry_data = {
        "producto_id": product_id,
        "cantidad_recibida": 100,
    }
    entry_response = test_client.post("/api/v1/inventario/entradas", json=entry_data)
    assert entry_response.status_code == 201
    lote_data = entry_response.json()
    lote_id = lote_data["id"]
    
    # El stock del producto es 100.

    # ETAPA 2: LA PRUEBA (Intentar sacar 101 unidades)
    exit_data = {
        "lote_id": lote_id,
        "cantidad": 101 # Uno mas de lo que hay
    }
    
    response = test_client.post("/api/v1/inventario/salidas", json=exit_data)
    
    # Esperamos 400 Bad Request, pero obtendremos 201 Created!
    assert response.status_code == 400
    
    # Verificamos el mensaje de error
    data = response.json()
    assert "detail" in data
    assert "insuficiente" in data["detail"].lower()

    # ETAPA 3: VERIFICACION
    # El stock del producto NO debe haber cambiado.
    product_response = test_client.get(f"/api/v1/productos/{product_id}")
    product_data = product_response.json()
    assert product_data["cantidad_actual"] == 100

def test_get_lote_by_id(test_client: TestClient, product_in_db: dict):
    """
    Prueba para GET /api/v1/inventario/lotes/{id} (Task 3.7).
    """
    product_id = product_in_db["id"]
    
    # ETAPA 1: SETUP - Registrar una ENTRADA para crear un lote
    entry_data = {
        "producto_id": product_id,
        "cantidad_recibida": 100,
        "fecha_vencimiento": (date.today() + timedelta(days=30)).isoformat()
    }
    entry_response = test_client.post("/api/v1/inventario/entradas", json=entry_data)
    assert entry_response.status_code == 201
    lote_data = entry_response.json()
    lote_id = lote_data["id"]

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    response = test_client.get(f"/api/v1/inventario/lotes/{lote_id}")

    # Esperamos 200 OK, pero obtendremos 404 Not Found
    assert response.status_code == 200
    
    # Verificamos la respuesta
    data = response.json()
    assert data["id"] == lote_id
    assert data["producto_id"] == product_id
    assert data["cantidad_actual"] == 100

def test_fefo_smart_dispatch(test_client: TestClient, product_in_db: dict):
    """
    Prueba el despachador inteligente FEFO (First Expired, First Out).
    (Task 3.10)
    """
    product_id = product_in_db["id"]
    
    # ETAPA 1: SETUP
    # Lote A (expira en 10 dias)
    entry_data_A = {
        "producto_id": product_id,
        "cantidad_recibida": 50,
        "fecha_vencimiento": (date.today() + timedelta(days=10)).isoformat()
    }
    response_A = test_client.post("/api/v1/inventario/entradas", json=entry_data_A)
    assert response_A.status_code == 201
    lote_A_id = response_A.json()["id"]

    # Lote B (expira en 30 dias)
    entry_data_B = {
        "producto_id": product_id,
        "cantidad_recibida": 50,
        "fecha_vencimiento": (date.today() + timedelta(days=30)).isoformat()
    }
    response_B = test_client.post("/api/v1/inventario/entradas", json=entry_data_B)
    assert response_B.status_code == 201
    lote_B_id = response_B.json()["id"]

    # Stock total del producto es 100 (50 + 50)

    # ETAPA 2: LA PRUEBA (Despachar 70 unidades)
    dispatch_data = {
        "producto_id": product_id,
        "cantidad": 70
    }
    
    response = test_client.post("/api/v1/inventario/despachar", json=dispatch_data)
    
    # Esperamos 200 OK, pero obtendremos 404 Not Found
    assert response.status_code == 200
    
    # Verificamos la respuesta (debe devolver los movimientos creados)
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 # Un movimiento por cada lote

    # ETAPA 3: VERIFICACION
    # 3.1: Lote A (expira primero) debe estar vacio
    lote_A_response = test_client.get(f"/api/v1/inventario/lotes/{lote_A_id}")
    assert lote_A_response.json()["cantidad_actual"] == 0 # 50 - 50
    
    # 3.2: Lote B (expira ultimo) debe tener 30
    lote_B_response = test_client.get(f"/api/v1/inventario/lotes/{lote_B_id}")
    assert lote_B_response.json()["cantidad_actual"] == 30 # 50 - 20
    
    # 3.3: Producto debe tener 30 en total
    product_response = test_client.get(f"/api/v1/productos/{product_id}")
    assert product_response.json()["cantidad_actual"] == 30 # 100 - 70