# sistema-inventarios/frontend/tests/test_callbacks.py
import pytest
from unittest.mock import Mock
from dash import html

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

def test_update_products_table_callback(mock_api_get):
    """
    Prueba el callback para actualizar la tabla de productos (Task 8.4).
    Usa el fixture 'mock_api_get'.
    """
    # ETAPA 1: SETUP
    # Configurar el fixture
    mock_response, _ = mock_api_get
    
    mock_api_response = [
        {
            "id": 1,
            "nombre": "Producto de Prueba",
            "sku": "SKU-TEST-001",
            "precio": 10.0,
            "cantidad_actual": 100,
            "stock_minimo": 10
        }
    ]
    mock_response.json.return_value = mock_api_response

    # ETAPA 2: LA PRUEBA
    from callbacks import update_products_table

    table_data, status_message = update_products_table(n_clicks=1)

    # ETAPA 3: VERIFICACION
    assert isinstance(table_data, list)
    assert status_message == "Datos cargados. 1 productos encontrados."
    assert len(table_data) == 1
    assert table_data[0]["sku"] == "SKU-TEST-001"

def test_navigation_callback():
    """
    Prueba el callback de navegacion principal (display_page).
    """
    # ETAPA 1: SETUP
    from layouts import products_layout

    # ETAPA 2: LA PRUEBA
    from callbacks import display_page

    # 1. Probar la pagina de productos
    page_content = display_page(pathname="/productos")
    assert page_content == products_layout

    # 2. Probar la pagina principal (Alertas)
    page_content = display_page(pathname="/")
    assert isinstance(page_content, html.P)

    # 3. Probar una pagina desconocida
    page_content = display_page(pathname="/pagina-mala")
    assert isinstance(page_content, html.P)