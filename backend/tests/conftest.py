# sistema-inventarios/backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Importamos los esquemas de Pydantic
import app.schemas.producto as product_schema
from datetime import datetime, date

# Import the models for our new fixtures
from app.models.producto import Producto
from app.models.lote import Lote

# Importamos la Base de nuestro codigo de aplicacion
from app.db.base import Base  
import app.models  # Importamos el paquete de modelos (ESTO ES VITAL)
from app.main import app  # Importar la app de FastAPI
from app.api.deps import get_db  # Importar la dependencia a sobreescribir

TEST_DATABASE_URL = "sqlite:///./test.db"

connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args=connect_args
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

@pytest.fixture(scope="function")
def product_in_db(test_client: TestClient) -> dict:
    """
    Fixture que crea un producto en la BD a traves de la API
    y devuelve los datos del producto creado (como un dict).
    """
    product_data = product_schema.ProductoCreate(
        nombre="Producto Fixture",
        sku="SKU-FIXTURE-001",
        precio=123.45,
        stock_minimo=5
    )
    response = test_client.post(
        "/api/v1/productos", 
        json=product_data.model_dump()
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def product_model_in_db(db_session: Session) -> Producto:
    """
    Fixture que crea un modelo Producto y lo guarda en la BD de prueba.
    Devuelve la instancia del modelo SQLAlchemy.
    """
    producto = Producto(
        nombre="Producto Modelo Fixture",
        sku="SKU-MODEL-001",
        precio=10.00,
        stock_minimo=10
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    return producto

@pytest.fixture(scope="function")
def lote_model_in_db(db_session: Session, product_model_in_db: Producto) -> Lote:
    """
    Fixture que crea un modelo Lote (depende de product_model_in_db)
    y lo guarda en la BD de prueba. Devuelve la instancia del Lote.
    """
    lote = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=50,
        fecha_vencimiento=date.today()
    )
    db_session.add(lote)
    db_session.commit()
    db_session.refresh(lote)
    return lote