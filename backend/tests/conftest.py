# sistema-inventarios/backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Importamos la Base de nuestro codigo de aplicacion
from app.db.base import Base  
import app.models  # Importamos el paquete de modelos (ESTO ES VITAL)
from app.main import app  # Importar la app de FastAPI
from app.api.deps import get_db  # Importar la dependencia a sobreescribir

# --- ESTA ES TU SOLUCIÓN ---
# Cambiamos de :memory: a un archivo para tener un estado persistente
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Fixture para pruebas de modelos (usa test.db)."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client() -> TestClient:
    """Fixture para pruebas de API (usa test.db)."""
    
    # 1. Crear las tablas
    Base.metadata.create_all(bind=engine)
    
    # 2. Definir el override
    def override_get_db() -> Session:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    # 3. Aplicar el override a la app
    app.dependency_overrides[get_db] = override_get_db
    
    # 4. Yield el cliente
    yield TestClient(app)
    
    # 5. Limpieza
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()