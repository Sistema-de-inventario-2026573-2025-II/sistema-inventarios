from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.producto import Producto
from app.models.lote import Lote
from app.models.alerta import Alerta # Nuevo import
from app.crud import crud_alerta # Nuevo import
from app.schemas.alerta import AlertaCreate # Nuevo import

def test_get_low_stock_alert(
    test_client: TestClient, 
    db_session: Session # Usar la sesion de BD para crear productos
):
    """
    Prueba el endpoint de alerta "Out of Stock".
    GET /api/v1/alertas/stock-minimo
    """
    # ETAPA 1: SETUP - Crear un producto bajo stock para generar una alerta
    producto_bajo_stock = Producto(
        nombre="Producto para Alerta Stock",
        sku="SKU-ALERT-STOCK",
        precio=10.00,
        cantidad_actual=5,
        stock_minimo=10
    )
    db_session.add(producto_bajo_stock)
    db_session.commit()
    db_session.refresh(producto_bajo_stock)

    # La primera llamada al endpoint activara la gestion de alertas
    # para crear la alerta de stock minimo
    response = test_client.get("/api/v1/alertas/stock-minimo")
    assert response.status_code == 200
    
    # ETAPA 2: LA PRUEBA - Llamar al endpoint nuevamente para obtener la alerta generada
    response = test_client.get("/api/v1/alertas/stock-minimo")

    assert response.status_code == 200
    
    # ETAPA 3: VERIFICACION
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Verificar que la alerta para nuestro producto bajo stock esta presente
    found_alert = False
    for alerta_dict in data:
        if (
            alerta_dict["tipo_alerta"] == "stock_minimo"
            and alerta_dict["entidad_id"] == producto_bajo_stock.id
            and alerta_dict["entidad_tipo"] == "producto"
            and alerta_dict["esta_activa"] == True
        ):
            found_alert = True
            assert "Producto para Alerta Stock" in alerta_dict["mensaje"]
            assert alerta_dict["metadata_json"]["sku"] == "SKU-ALERT-STOCK"
            break
    assert found_alert, "No se encontro la alerta de stock minimo para el producto creado"


def test_get_expiring_lotes_alert(
    test_client: TestClient, 
    db_session: Session # Usar la sesion de BD para crear lotes
):
    """
    Prueba el endpoint de alerta "Por Vencer".
    GET /api/v1/alertas/por-vencer
    """
    # ETAPA 1: SETUP - Crear un lote que expira para generar una alerta
    producto_base = Producto(
        nombre="Producto para Lote Vencimiento",
        sku="SKU-LOTE-VENCE",
        precio=10.00,
        cantidad_actual=10,
        stock_minimo=0
    )
    db_session.add(producto_base)
    db_session.commit()
    db_session.refresh(producto_base)

    lote_expirando = Lote(
        producto_id=producto_base.id,
        cantidad_recibida=10,
        cantidad_actual=10,
        fecha_vencimiento=(date.today() + timedelta(days=15))
    )
    db_session.add(lote_expirando)
    db_session.commit()
    db_session.refresh(lote_expirando)

    # La primera llamada al endpoint activara la gestion de alertas
    # para crear la alerta de lote por vencer
    response = test_client.get("/api/v1/alertas/por-vencer?days=30")
    assert response.status_code == 200

    # ETAPA 2: LA PRUEBA - Llamar al endpoint nuevamente para obtener la alerta generada
    response = test_client.get("/api/v1/alertas/por-vencer?days=30")

    assert response.status_code == 200
    
    # ETAPA 3: VERIFICACION
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Verificar que la alerta para nuestro lote por vencer esta presente
    found_alert = False
    for alerta_dict in data:
        if (
            alerta_dict["tipo_alerta"] == "por_vencer_30"
            and alerta_dict["entidad_id"] == lote_expirando.id
            and alerta_dict["entidad_tipo"] == "lote"
            and alerta_dict["esta_activa"] == True
        ):
            found_alert = True
            assert "Lote Vencimiento" in alerta_dict["mensaje"]
            assert alerta_dict["metadata_json"]["producto_sku"] == "SKU-LOTE-VENCE"
            break
    assert found_alert, "No se encontro la alerta de lote por vencer para el lote creado"