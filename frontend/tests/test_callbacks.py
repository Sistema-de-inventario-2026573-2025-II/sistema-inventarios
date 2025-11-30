# sistema-inventarios/frontend/tests/test_callbacks.py
import pytest
from unittest.mock import Mock, call
from dash import html
from layouts import products_layout, alerts_layout


class ApiClientMock:
    """
    Clase auxiliar para crear un mock del cliente API (requests).
    Permite añadir respuestas en cola y verificar las llamadas.
    """
    def __init__(self, mocker):
        self.mocker = mocker
        self._responses = []
        self.patch = None

    def add_response(self, json_data, status_code=200):
        """Añade una respuesta simulada a la cola."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        self._responses.append(mock_response)

    def start(self):
        """Inicia el 'patch' con las respuestas configuradas."""
        self.patch = self.mocker.patch(
            "callbacks.requests.get", 
            side_effect=self._responses
        )
        return self.patch
        
    def assert_has_calls(self, calls, any_order=False):
        """Verifica que se hicieron las llamadas esperadas."""
        self.patch.assert_has_calls(calls, any_order=any_order)


@pytest.fixture
def mock_api_client(mocker):
    """
    Fixture de Pytest que proporciona una instancia de ApiClientMock
    para simplificar la simulación de llamadas a la API.
    """
    return ApiClientMock(mocker)


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
    mock_api_client.start()

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


def test_update_alerts_dashboard(mock_api_client):
    """
    Prueba el callback del dashboard de alertas (Task 8.6 - Refactor).
    Debe llamar a dos endpoints y devolver dos listas de datos.
    """
    # ETAPA 1: SETUP
    # Configurar las respuestas simuladas de la API en orden
    mock_api_client.add_response(
        json_data=[{"sku": "SKU-LOW-001", "cantidad_actual": 1}]
    )
    mock_api_client.add_response(
        json_data=[{"id": 99, "cantidad_actual": 5}]
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
    
    # 3.2: Verificar los datos devueltos
    assert low_stock_data[0]["sku"] == "SKU-LOW-001"
    assert expiring_data[0]["id"] == 99
    
    # 3.3: Verificar los mensajes de estado
    assert "1 productos" in low_stock_msg
    assert "1 lotes" in expiring_msg