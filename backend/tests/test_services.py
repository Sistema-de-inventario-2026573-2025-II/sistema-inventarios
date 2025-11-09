# sistema-inventarios/backend/tests/test_services.py
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.models.lote import Lote
from datetime import date, timedelta

def test_check_stock_minimo_service(db_session: Session):
    """
    Prueba el servicio de alerta "Out of Stock" (Task 4.1).
    """
    # ETAPA 1: SETUP
    # Crear un producto que este por debajo de su stock minimo
    producto_bajo_stock = Producto(
        nombre="Producto Bajo Stock",
        sku="SKU-LOW-001",
        precio=10.00,
        cantidad_actual=5,
        stock_minimo=10  # <-- Stock (5) < Minimo (10)
    )
    # Crear un producto que este bien
    producto_ok = Producto(
        nombre="Producto OK",
        sku="SKU-OK-001",
        precio=10.00,
        cantidad_actual=50,
        stock_minimo=10
    )
    db_session.add_all([producto_bajo_stock, producto_ok])
    db_session.commit()

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    
    # Esta importacion fallara
    from app.services.alerts import check_stock_minimo

    productos_alerta = check_stock_minimo(db=db_session)

    # ETAPA 3: VERIFICACION
    assert isinstance(productos_alerta, list)
    assert len(productos_alerta) == 1
    assert productos_alerta[0].sku == "SKU-LOW-001"

def test_check_expiring_lotes_service(db_session: Session, product_model_in_db: Producto):
    """
    Prueba el servicio de alerta "Por Vencer" (expiring soon).
    """
    # ETAPA 1: SETUP
    # product_model_in_db nos da un producto base
    
    # Lote A: Expira en 15 dias (DEBE ser encontrado)
    lote_expirando = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        fecha_vencimiento=(date.today() + timedelta(days=15))
    )
    
    # Lote B: Expira en 60 dias (NO debe ser encontrado)
    lote_ok = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        fecha_vencimiento=(date.today() + timedelta(days=60))
    )
    
    # Lote C: Sin fecha de vencimiento (NO debe ser encontrado)
    lote_sin_fecha = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        fecha_vencimiento=None
    )
    
    db_session.add_all([lote_expirando, lote_ok, lote_sin_fecha])
    db_session.commit()

    # ETAPA 2: LA PRUEBA (Esto es lo que fallara)
    
    # Esta importacion fallara
    from app.services.alerts import check_lotes_por_vencer

    # Probamos con un umbral de 30 dias
    lotes_en_alerta = check_lotes_por_vencer(db=db_session, days_threshold=30)

    # ETAPA 3: VERIFICACION
    assert isinstance(lotes_en_alerta, list)
    assert len(lotes_en_alerta) == 1
    assert lotes_en_alerta[0].id == lote_expirando.id