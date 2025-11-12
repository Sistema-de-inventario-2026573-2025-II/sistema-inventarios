# sistema-inventarios/backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Importamos los esquemas de Pydantic
import app.schemas.producto as product_schema
from datetime import datetime, date, timedelta

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

@pytest.fixture(scope="function")
def low_stock_product_setup(test_client: TestClient) -> dict:
    """
    Fixture que crea un producto que esta por debajo
    de su stock minimo.
    """
    product_data = {
        "nombre": "Producto de Prueba de Alerta",
        "sku": "SKU-ALERT-001",
        "precio": 1.00,
        "stock_minimo": 5
    }
    # Por defecto, cantidad_actual es 0.
    # 0 < 5, asi que esta en alerta.
    response_create = test_client.post("/api/v1/productos", json=product_data)
    assert response_create.status_code == 201
    
    return response_create.json()

@pytest.fixture(scope="function")
def expiring_lotes_setup(test_client: TestClient, product_in_db: dict) -> dict:
    """
    Fixture que crea un setup complejo para pruebas de alertas:
    - 1 Producto (del fixture 'product_in_db')
    - 1 Lote que expira en 15 dias ("lote_a")
    - 1 Lote que expira en 60 dias ("lote_b")
    Devuelve un dict con los IDs de los objetos creados.
    """
    product_id = product_in_db["id"]
    
    # Lote A: Expira en 15 dias
    lote_expirando_data = {
        "producto_id": product_id,
        "cantidad_recibida": 10,
        "fecha_vencimiento": (date.today() + timedelta(days=15)).isoformat()
    }
    resp_a = test_client.post("/api/v1/inventario/entradas", json=lote_expirando_data)
    assert resp_a.status_code == 201
    lote_a_id = resp_a.json()["id"]

    # Lote B: Expira en 60 dias
    lote_ok_data = {
        "producto_id": product_id,
        "cantidad_recibida": 10,
        "fecha_vencimiento": (date.today() + timedelta(days=60)).isoformat()
    }
    resp_b = test_client.post("/api/v1/inventario/entradas", json=lote_ok_data)
    assert resp_b.status_code == 201
    lote_b_id = resp_b.json()["id"]
    
    # Devolver los IDs para que el test los use
    yield {
        "product_id": product_id,
        "lote_a_id": lote_a_id,
        "lote_b_id": lote_b_id
    }