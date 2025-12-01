from sqlalchemy.orm import Session
from app.models.producto import Producto

def test_top_available_products_report(db_session: Session):
    """
    Prueba el reporte de los productos con mayor disponibilidad (Task 5.1).
    """
    # ETAPA 1: SETUP
    # Crear varios productos con diferentes cantidades actuales
    productos = [
        Producto(nombre="Producto A", sku="SKU-A", precio=10.00, cantidad_actual=50, stock_minimo=10),
        Producto(nombre="Producto B", sku="SKU-B", precio=15.00, cantidad_actual=20, stock_minimo=5),
        Producto(nombre="Producto C", sku="SKU-C", precio=20.00, cantidad_actual=80, stock_minimo=15),
        Producto(nombre="Producto D", sku="SKU-D", precio=25.00, cantidad_actual=10, stock_minimo=2),
    ]
    db_session.add_all(productos)
    db_session.commit()

    # ETAPA 2: LA PRUEBA
    from app.services.reports import get_top_available_products

    top_products = get_top_available_products(db=db_session, top_n=3)

    # ETAPA 3: VERIFICACION
    assert isinstance(top_products, list)
    assert len(top_products) == 3
    assert top_products[0].sku == "SKU-C"  # Cantidad 80
    assert top_products[1].sku == "SKU-A"  # Cantidad 50
    assert top_products[2].sku == "SKU-B"  # Cantidad 20