# sistema-inventarios/frontend/tests/conftest.py
import pytest
from unittest.mock import patch, Mock, call


@pytest.fixture
def mock_callback_context():
    """
    Fixture to mock dash.callback_context.
    Usage:
        def test_my_callback(mock_callback_context):
            mock_callback_context.triggered = [{'prop_id': 'my-button.n_clicks'}]
            ...
    """
    with patch("callbacks.dash.callback_context") as mock_context:
        yield mock_context


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

    def start(self, method="get"):
        """Inicia el 'patch' con las respuestas configuradas."""
        self.patch = self.mocker.patch(
            f"callbacks.requests.{method}",
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
