# sistema-inventarios/backend/tests/test_services.py
from sqlalchemy.orm import Session
from app.models.producto import Producto
from app.models.lote import Lote
from app.models.alerta import Alerta
from app.crud import crud_alerta
from app.schemas.alerta import AlertaCreate
from datetime import date, timedelta
from app.core.cache import cache # Importamos cache para invalidar

def test_check_stock_minimo_service(db_session: Session):
    """
    Prueba el servicio que gestiona las alertas de stock minimo.
    """
    # ETAPA 1: SETUP INICIAL: Crear productos
    producto_bajo_stock = Producto(
        nombre="Producto Bajo Stock Inicial",
        sku="SKU-LOW-001",
        precio=10.00,
        cantidad_actual=5,
        stock_minimo=10
    )
    producto_ok = Producto(
        nombre="Producto OK Inicial",
        sku="SKU-OK-001",
        precio=10.00,
        cantidad_actual=50,
        stock_minimo=10
    )
    db_session.add_all([producto_bajo_stock, producto_ok])
    db_session.commit()
    db_session.refresh(producto_bajo_stock)
    db_session.refresh(producto_ok)

    from app.services.alerts import check_stock_minimo

    # --- PRIMERA EJECUCION: DEBE CREAR UNA ALERTA ---
    # Asegurarse de que el cache esta limpio al inicio para la primera ejecucion
    cache.delete("alert_stock_minimo") 
    check_stock_minimo(db=db_session)

    # VERIFICACION 1: Se ha creado una alerta para el producto bajo stock
    alertas_creadas = db_session.query(Alerta).filter(
        Alerta.entidad_id == producto_bajo_stock.id,
        Alerta.tipo_alerta == "stock_minimo",
        Alerta.entidad_tipo == "producto",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_creadas) == 1
    assert "SKU-LOW-001" in alertas_creadas[0].mensaje
    assert alertas_creadas[0].metadata_json["sku"] == "SKU-LOW-001"

    # --- SEGUNDA EJECUCION: NO DEBE CREAR ALERTAS DUPLICADAS ---
    # El cache se invalida dentro de la funcion check_stock_minimo,
    # asi que no es necesario invalidarlo aqui de nuevo.
    check_stock_minimo(db=db_session)
    alertas_duplicadas = db_session.query(Alerta).filter(
        Alerta.entidad_id == producto_bajo_stock.id,
        Alerta.tipo_alerta == "stock_minimo",
        Alerta.entidad_tipo == "producto",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_duplicadas) == 1 # Sigue siendo solo una

    # --- TERCERA EJECUCION: PRODUCTO VUELVE A ESTAR OK, ALERTA DEBE DESACTIVARSE ---
    producto_bajo_stock.cantidad_actual = 15 # Ahora esta OK
    db_session.add(producto_bajo_stock)
    db_session.commit()
    db_session.refresh(producto_bajo_stock)

    check_stock_minimo(db=db_session)

    # VERIFICACION 3: La alerta original debe estar desactivada
    alerta_desactivada = db_session.query(Alerta).filter(
        Alerta.id == alertas_creadas[0].id
    ).first()
    assert alerta_desactivada.esta_activa == False

    # VERIFICACION 4: No debe haber alertas activas para este producto
    alertas_activas_final = db_session.query(Alerta).filter(
        Alerta.entidad_id == producto_bajo_stock.id,
        Alerta.tipo_alerta == "stock_minimo",
        Alerta.entidad_tipo == "producto",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_activas_final) == 0

    # Asegurarse de que el producto "OK" nunca tuvo alertas
    alertas_producto_ok = db_session.query(Alerta).filter(
        Alerta.entidad_id == producto_ok.id,
        Alerta.tipo_alerta == "stock_minimo",
        Alerta.entidad_tipo == "producto",
    ).all()
    assert len(alertas_producto_ok) == 0



def test_check_expiring_lotes_service(db_session: Session, product_model_in_db: Producto):
    """
    Prueba el servicio que gestiona las alertas de lotes por vencer.
    """
    # ETAPA 1: SETUP INICIAL: Crear lotes
    # Lote A: Expira en 15 dias (DEBE generar alerta)
    lote_expirando = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        cantidad_actual=10,
        fecha_vencimiento=(date.today() + timedelta(days=15))
    )
    
    # Lote B: Expira en 60 dias (NO debe generar alerta con umbral de 30)
    lote_ok = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        cantidad_actual=10,
        fecha_vencimiento=(date.today() + timedelta(days=60))
    )
    
    # Lote C: Sin fecha de vencimiento (NO debe generar alerta)
    lote_sin_fecha = Lote(
        producto_id=product_model_in_db.id,
        cantidad_recibida=10,
        cantidad_actual=10,
        fecha_vencimiento=None
    )
    
    db_session.add_all([lote_expirando, lote_ok, lote_sin_fecha])
    db_session.commit()
    db_session.refresh(lote_expirando)
    db_session.refresh(lote_ok)
    db_session.refresh(lote_sin_fecha)

    from app.services.alerts import check_lotes_por_vencer_and_manage_alerts

    # --- PRIMERA EJECUCION: DEBE CREAR UNA ALERTA ---
    # Asegurarse de que el cache esta limpio al inicio para la primera ejecucion
    cache.delete("alert_lotes_vencimiento_30") 
    check_lotes_por_vencer_and_manage_alerts(db=db_session, days_threshold=30)

    # VERIFICACION 1: Se ha creado una alerta para el lote expirando
    alertas_creadas = db_session.query(Alerta).filter(
        Alerta.entidad_id == lote_expirando.id,
        Alerta.tipo_alerta == "por_vencer_30",
        Alerta.entidad_tipo == "lote",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_creadas) == 1
    assert alertas_creadas[0].metadata_json["producto_nombre"] == product_model_in_db.nombre
    assert alertas_creadas[0].metadata_json["producto_sku"] == product_model_in_db.sku
    assert alertas_creadas[0].metadata_json["fecha_vencimiento"] == str(lote_expirando.fecha_vencimiento)
    assert alertas_creadas[0].metadata_json["producto_sku"] == product_model_in_db.sku

    # --- SEGUNDA EJECUCION: NO DEBE CREAR ALERTAS DUPLICADAS ---
    cache.delete("alert_lotes_vencimiento_30") 
    check_lotes_por_vencer_and_manage_alerts(db=db_session, days_threshold=30)
    alertas_duplicadas = db_session.query(Alerta).filter(
        Alerta.entidad_id == lote_expirando.id,
        Alerta.tipo_alerta == "por_vencer_30",
        Alerta.entidad_tipo == "lote",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_duplicadas) == 1 # Sigue siendo solo una

    # --- TERCERA EJECUCION: LOTE YA NO ESTA POR VENCER (simulacion), ALERTA DEBE DESACTIVARSE ---
    # Simulamos que el lote ya no cumple la condicion de alerta cambiando su fecha de vencimiento
    lote_expirando.fecha_vencimiento = date.today() + timedelta(days=90) # Ahora vence mas tarde
    db_session.add(lote_expirando)
    db_session.commit()
    db_session.refresh(lote_expirando)

    cache.delete("alert_lotes_vencimiento_30") 
    check_lotes_por_vencer_and_manage_alerts(db=db_session, days_threshold=30)

    # VERIFICACION 3: La alerta original debe estar desactivada
    alerta_desactivada = db_session.query(Alerta).filter(
        Alerta.id == alertas_creadas[0].id
    ).first()
    assert alerta_desactivada.esta_activa == False

    # VERIFICACION 4: No debe haber alertas activas para este lote
    alertas_activas_final = db_session.query(Alerta).filter(
        Alerta.entidad_id == lote_expirando.id,
        Alerta.tipo_alerta == "por_vencer_30",
        Alerta.entidad_tipo == "lote",
        Alerta.esta_activa == True
    ).all()
    assert len(alertas_activas_final) == 0

    # Asegurarse de que los lotes "OK" nunca tuvieron alertas para este umbral
    alertas_lote_ok = db_session.query(Alerta).filter(
        Alerta.entidad_id == lote_ok.id,
        Alerta.tipo_alerta == "por_vencer_30",
        Alerta.entidad_tipo == "lote",
    ).all()
    assert len(alertas_lote_ok) == 0
    
    alertas_lote_sin_fecha = db_session.query(Alerta).filter(
        Alerta.entidad_id == lote_sin_fecha.id,
        Alerta.tipo_alerta == "por_vencer_30",
        Alerta.entidad_tipo == "lote",
    ).all()
    assert len(alertas_lote_sin_fecha) == 0