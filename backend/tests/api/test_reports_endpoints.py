from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.producto import Producto

def test_top_available_products_response(test_client: TestClient, db_session: Session):
    """
    Prueba el endpoint de reporte de los productos con mayor disponibilidad.
    GET /api/v1/reports/top-productos-disponibles
    """
    # ETAPA 1: SETUP - Crear varios productos con diferentes cantidades actuales
    productos = [
        Producto(nombre="Producto A", sku="SKU-A", precio=10.00, cantidad_actual=50, stock_minimo=10),
        Producto(nombre="Producto B", sku="SKU-B", precio=15.00, cantidad_actual=20, stock_minimo=5),
        Producto(nombre="Producto C", sku="SKU-C", precio=20.00, cantidad_actual=80, stock_minimo=15),
        Producto(nombre="Producto D", sku="SKU-D", precio=25.00, cantidad_actual=10, stock_minimo=2),
    ]
    db_session.add_all(productos)
    db_session.commit()

    # ETAPA 2: LA PRUEBA - Llamar al endpoint del reporte
    response = test_client.get("/api/v1/reportes/top-productos-disponibles?top_n=3")
    assert response.status_code == 200

    # ETAPA 3: VERIFICACION
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["sku"] == "SKU-C"  # Cantidad 80
    assert data[1]["sku"] == "SKU-A"  # Cantidad 50
    assert data[2]["sku"] == "SKU-B"  # Cantidad 20