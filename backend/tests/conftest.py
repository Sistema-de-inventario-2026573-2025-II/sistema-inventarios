# sistema-inventarios/backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Importamos la Base de nuestro codigo de aplicacion
from app.db.base import Base  

# Configuracion de la BD de prueba (en memoria)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Fixture de Pytest para crear una sesion de BD de prueba (en memoria).
    Crea todas las tablas antes de la prueba y las borra despues.
    """
    # Creamos todas las tablas definidas en app/db/base.py
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Borramos todas las tablas para la proxima prueba
        Base.metadata.drop_all(bind=engine)