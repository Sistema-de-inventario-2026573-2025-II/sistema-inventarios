# sistema-inventarios/backend/tests/test_db_setup.py
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text

def test_db_session_fixture(db_session: Session):
    """
    Prueba que el fixture 'db_session' existe, es del tipo correcto
    y puede conectarse a la base de datos.
    """
    assert db_session is not None
    assert isinstance(db_session, Session)
    
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1