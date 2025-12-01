# sistema-inventarios/frontend/tests/test_callbacks.py
import pytest
from unittest.mock import call
from dash import html
import frontend.layouts as layouts # Import all layouts from frontend.layouts


def test_dash_app_import():
    """
    Prueba de humo para la app de Dash (Task 8.2).
    """
    try:
        from dashboard import app
        assert app is not None
    except ImportError as e:
        assert False, f"Fallo la importacion de la app Dash: {e}"

@pytest.mark.parametrize(
    "trigger_id, n_clicks, n_intervals",
    [
        ('refresh-products-button.n_clicks', 1, 0),
        ('products-interval.n_intervals', 0, 1),
    ]
)
def test_update_products_table_callback(
    mock_api_client, mock_callback_context, trigger_id, n_clicks, n_intervals
):
    """
    Prueba el callback para actualizar la tabla de productos (Task 8.6 - Refactor).
    Debe funcionar tanto por boton (manual) como por intervalo (auto).
    """
    # ETAPA 1: SETUP
    mock_api_response = [
        {
            "id": 1,
            "nombre": "Producto de Prueba",
            "sku": "SKU-TEST-001",
        }
    ]
    mock_api_client.add_response(json_data=mock_api_response)
    mock_api_client.start(method="get")

    # Configurar el contexto simulado para el trigger actual
    mock_callback_context.triggered = [{'prop_id': trigger_id}]

    # ETAPA 2: LA PRUEBA
    from callbacks import update_products_table
    table_data, msg = update_products_table(
        n_clicks=n_clicks, n_intervals=n_intervals
    )
    
    # ETAPA 3: VERIFICACION
    assert len(table_data) == 1
    assert table_data[0]["nombre"] == "Producto de Prueba"
    assert "1 productos" in msg
    mock_api_client.patch.assert_called_once()

def test_navigation_callback():
    """
    Prueba el callback de navegacion principal (display_page).
    """
    # ETAPA 1: SETUP
    # No es necesario importar 'layouts' aquí para la prueba de navegacion,
    # ya que display_page importa el modulo completo.

    # ETAPA 2: LA PRUEBA
    from callbacks import display_page

    # 1. Probar la pagina de productos
    page_content = display_page(pathname="/productos")
    assert page_content.id == layouts.products_layout.id

    # 2. Probar la pagina de inventario
    page_content = display_page(pathname="/inventario")
    assert page_content.id == layouts.inventory_layout.id

    # 3. Probar la pagina de reportes
    page_content = display_page(pathname="/reportes")
    assert page_content.id == layouts.reports_layout.id

    # 4. Probar la pagina principal (Alertas)
    page_content = display_page(pathname="/")
    assert page_content.id == layouts.alerts_layout.id

    # 5. Probar una pagina desconocida (debe ir a la pagina de Alertas)
    page_content = display_page(pathname="/pagina-mala")
    assert page_content.id == layouts.alerts_layout.id


def test_update_alerts_dashboard(mock_api_client):
    """
    Prueba el callback del dashboard de alertas.
    Debe llamar a dos endpoints y devolver dos listas de datos procesados.
    """
    # ETAPA 1: SETUP
    # Configurar las respuestas simuladas de la API en orden (AlertaInDB schema)
    mock_api_client.add_response(
        json_data=[
            {
                "id": 1,
                "tipo_alerta": "stock_minimo",
                "entidad_id": 101,
                "entidad_tipo": "producto",
                "mensaje": "Alerta de stock minimo para Producto Test",
                "fecha_creacion": "2025-01-01T12:00:00",
                "esta_activa": True,
                "metadata_json": {
                    "nombre": "Producto Test",
                    "sku": "SKU-TEST-001",
                    "cantidad_actual": 5,
                    "stock_minimo": 10
                }
            }
        ]
    )
    mock_api_client.add_response(
        json_data=[
            {
                "id": 2,
                "tipo_alerta": "por_vencer_30",
                "entidad_id": 201,
                "entidad_tipo": "lote",
                "mensaje": "Alerta de lote por vencer para Lote Test",
                "fecha_creacion": "2025-01-01T12:00:00",
                "esta_activa": True,
                "metadata_json": {
                    "producto_nombre": "Producto Lote Test",
                    "producto_sku": "SKU-LOTE-TEST",
                    "cantidad_actual": 20,
                    "fecha_vencimiento": "2025-01-30"
                }
            }
        ]
    )
    mock_get = mock_api_client.start()

    # ETAPA 2: LA PRUEBA
    from callbacks import update_alerts_dashboard

    (
        low_stock_data, 
        expiring_data, 
        low_stock_msg, 
        expiring_msg
    ) = update_alerts_dashboard(pathname="/")

    # ETAPA 3: VERIFICACION
    # 3.1: Verificar que se llamo a los endpoints correctos
    expected_calls = [
        call("http://127.0.0.1:8000/api/v1/alertas/stock-minimo"),
        call("http://127.0.0.1:8000/api/v1/alertas/por-vencer?days=30")
    ]
    mock_api_client.assert_has_calls(expected_calls)
    
    # 3.2: Verificar los datos devueltos procesados
    assert len(low_stock_data) == 1
    assert low_stock_data[0]["id"] == 1
    assert low_stock_data[0]["sku"] == "SKU-TEST-001"
    assert "Alerta de stock minimo" in low_stock_data[0]["mensaje"]

    assert len(expiring_data) == 1
    assert expiring_data[0]["id"] == 2
    assert expiring_data[0]["entidad_id"] == 201
    assert expiring_data[0]["producto_sku"] == "SKU-LOTE-TEST"
    assert "Alerta de lote por vencer" in expiring_data[0]["mensaje"]
    
    # 3.3: Verificar los mensajes de estado
    assert "1 alertas de stock mínimo" in low_stock_msg
    assert "1 alertas de lotes por vencer" in expiring_msg
    
def test_register_inventory_entry_callback(mock_api_client):

    """
    Prueba el callback para registrar una nueva entrada de inventario (lote).
    Debe devolver un mensaje de exito cuando la API responde correctamente.
    """

    # ETAPA 1: SETUP    
    # Simulamos una respuesta exitosa de la API al crear un lote

    mock_api_client.add_response(
        json_data={"id": 100, "producto_id": 1, "cantidad_actual": 50},
        status_code=201
    )

    mock_post = mock_api_client.start(method="post") # Usaremos POST esta vez

    # ETAPA 2: LA PRUEBA
    from callbacks import register_inventory_entry

    # Llamamos al callback con datos de prueba
    result_message, result_color = register_inventory_entry(
        n_clicks=1,
        product_id=1,
        quantity=50,
        expiration_date="2025-12-31"
    )

    # ETAPA 3: VERIFICACION
    # 3.1: Verificar que se hizo la llamada POST correcta
    mock_post.assert_called_once()

    # 3.2: Verificar el mensaje de exito
    assert "Lote registrado con éxito" in result_message
    assert result_color == "success"
        
        
def test_register_simple_dispatch_callback(mock_api_client):
    """
    Prueba el callback para registrar una salida simple por lote_id.
    """
    # SETUP
    mock_api_client.add_response(
        json_data={"message": "Salida registrada con éxito"},
        status_code=201 # Fix: Changed from 200 to 201
    )
    mock_post = mock_api_client.start(method="post")

    # TEST
    from callbacks import register_simple_dispatch
    result_message, result_color = register_simple_dispatch(1, 10, 5)

    # VERIFY
    mock_post.assert_called_once()
    assert "Salida registrada con éxito" in result_message
    assert result_color == "success"
        
        
def test_register_fefo_dispatch_callback(mock_api_client):
    """
    Prueba el callback para registrar una salida FEFO.
    """
    # SETUP
    mock_api_client.add_response(
        json_data={"message": "Salida FEFO registrada con éxito"},
        status_code=200
    )
    mock_post = mock_api_client.start(method="post")

    # TEST
    from callbacks import register_fefo_dispatch
    result_message, result_color = register_fefo_dispatch(1, 1, 20)

    # VERIFY
    mock_post.assert_called_once()
    assert "Salida FEFO registrada con éxito" in result_message
    assert result_color == "success"
        