# sistema-inventarios/frontend/tests/conftest.py
import pytest
from unittest.mock import patch

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
