def test_app_import() -> None:
    """
    Smoke test: Can we import the 'app' object from 'app.main'?
    """
    try:
        from app.main import app
        assert app is not None, "'app' object is None"
    except ImportError as e:
        assert False, f"Failed to import 'app' from 'app.main': {e}"