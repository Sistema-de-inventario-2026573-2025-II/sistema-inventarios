from fastapi.testclient import TestClient
from datetime import date, timedelta

def test_get_low_stock_alert(
    test_client: TestClient, 
    low_stock_product_setup: dict # <-- Inyectar nuevo fixture
):
    """
    Prueba el endpoint de alerta "Out of Stock".
    GET /api/v1/alertas/stock-minimo (Task 4.5.1)
    """
    # ETAPA 1: SETUP
    created_product = low_stock_product_setup

    # ETAPA 2: LA PRUEBA
    response = test_client.get("/api/v1/alertas/stock-minimo")

    assert response.status_code == 200
    
    # ETAPA 3: VERIFICACION
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    found = any(p["id"] == created_product["id"] for p in data)
    assert found, "El producto creado no se encontro en la lista de alertas"

def test_get_expiring_lotes_alert(
    test_client: TestClient, 
    expiring_lotes_setup: dict  # <-- Inyectar nuestro nuevo fixture
):
    """
    Prueba el endpoint de alerta "Por Vencer".
    GET /api/v1/alertas/por-vencer
    """
    # ETAPA 1: SETUP
    lote_a_id = expiring_lotes_setup["lote_a_id"]

    # ETAPA 2: LA PRUEBA
    # Probamos con un umbral de 30 dias
    response = test_client.get("/api/v1/alertas/por-vencer?days=30")

    assert response.status_code == 200
    
    # ETAPA 3: VERIFICACION
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == lote_a_id