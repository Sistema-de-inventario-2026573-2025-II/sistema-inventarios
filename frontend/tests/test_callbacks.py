# sistema-inventarios/frontend/tests/test_callbacks.py
import pytest
from unittest.mock import Mock, call
from dash import html
from layouts import products_layout, alerts_layout

@pytest.fixture
def mock_api_get(mocker):
    """
    Fixture de Pytest para "mockear" una llamada GET a la API
    y devolver una respuesta controlada.
    """
    # 1. Crear el objeto que "falsificara" la respuesta
    mock_response = Mock()
    mock_response.status_code = 200
    
    # 2. "Patch" (interceptar) la llamada 'requests.get'
    mock_patch = mocker.patch("callbacks.requests.get", return_value=mock_response)
    
    # 3. Devolver ambos para que el test pueda usarlos
    # (El mock_response para configurar la data,
    # y el mock_patch para verificar que fue llamado)
    yield mock_response, mock_patch

def test_dash_app_import():
    """
    Prueba de humo para la app de Dash (Task 8.2).
    """
    try:
        from dashboard import app
        assert app is not None
    except ImportError as e:
        assert False, f"Fallo la importacion de la app Dash: {e}"

def test_update_products_table_callback(mock_api_get, mocker):
    """
    Prueba el callback para actualizar la tabla de productos.
    Debe funcionar tanto por boton (manual) como por intervalo (auto).
    (Task 8.5)
    """
    # ETAPA 1: SETUP
    mock_response, _ = mock_api_get
    
    mock_api_response = [
        {
            "id": 1,
            "nombre": "Producto de Prueba",
            "sku": "SKU-TEST-001",
            # ... resto de campos
        }
    ]
    mock_response.json.return_value = mock_api_response

    # ETAPA 2: LA PRUEBA
    from callbacks import update_products_table

    # Mockear el dash.callback_context para simular los triggers
    mock_ctx = mocker.patch("callbacks.dash.callback_context")

    # CASO A: Disparo manual (boton)
    # Simular que el boton fue el que disparo el callback
    mock_ctx.triggered = [{'prop_id': 'refresh-products-button.n_clicks'}]
    # n_clicks=1, n_intervals=0
    table_data, msg = update_products_table(n_clicks=1, n_intervals=0)
    assert len(table_data) == 1
    assert "1 productos" in msg

    # CASO B: Disparo automatico (intervalo/carga inicial)
    # Simular que el intervalo fue el que disparo el callback
    mock_ctx.triggered = [{'prop_id': 'products-interval.n_intervals'}]
    # n_clicks=None (o 0), n_intervals=1
    table_data_auto, msg_auto = update_products_table(n_clicks=0, n_intervals=1)
    
    # ETAPA 3: VERIFICACION
    # Debe devolver los mismos datos
    assert table_data_auto == table_data
    assert msg_auto == msg

def test_navigation_callback():
    """
    Prueba el callback de navegacion principal (display_page).
    """
    # ETAPA 1: SETUP
    # (No es necesario importar 'layouts' aquí, ya está arriba)

    # ETAPA 2: LA PRUEBA
    # Importar desde la ubicacion correcta
    from callbacks import display_page

    # 1. Probar la pagina de productos
    page_content = display_page(pathname="/productos")
    assert page_content == products_layout

    # 2. Probar la pagina principal (Alertas)
    page_content = display_page(pathname="/")
    assert page_content == alerts_layout  # <-- ESTA ES LA CORRECCIÓN

    # 3. Probar una pagina desconocida (debe ir a la pagina de Alertas)
    page_content = display_page(pathname="/pagina-mala")
    assert page_content == alerts_layout # <-- ESTA ES LA CORRECCIÓN 


def test_update_alerts_dashboard(mocker):
    """
    Prueba el callback del dashboard de alertas (Task 8.x).
    Debe llamar a dos endpoints y devolver dos listas de datos.
    """
    # ETAPA 1: SETUP
    # Mockear dos respuestas de API diferentes
    mock_low_stock_data = [{"sku": "SKU-LOW-001", "cantidad_actual": 1}]
    mock_expiring_data = [{"id": 99, "cantidad_actual": 5}]

    # Crear los objetos de respuesta
    mock_low_stock_response = Mock(status_code=200)
    mock_low_stock_response.json.return_value = mock_low_stock_data
    
    mock_expiring_response = Mock(status_code=200)
    mock_expiring_response.json.return_value = mock_expiring_data

    # Usamos mocker.patch con 'side_effect' para que devuelva
    # un valor diferente cada vez que se llama.
    mock_get = mocker.patch(
        "callbacks.requests.get", 
        side_effect=[mock_low_stock_response, mock_expiring_response]
    )

    # ETAPA 2: LA PRUEBA
    from callbacks import update_alerts_dashboard

    # El callback se dispara con la URL de la pagina
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
    mock_get.assert_has_calls(expected_calls)
    
    # 3.2: Verificar los datos devueltos
    assert low_stock_data[0]["sku"] == "SKU-LOW-001"
    assert expiring_data[0]["id"] == 99
    
    # 3.3: Verificar los mensajes de estado
    assert "1 productos" in low_stock_msg
    assert "1 lotes" in expiring_msg