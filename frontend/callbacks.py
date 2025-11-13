import logging
import requests
from dash import callback, Output, Input, State, no_update, html
from dashboard import app
from ui_config import get_frontend_settings
from layouts import products_layout

logger = logging.getLogger(__name__)

settings = get_frontend_settings()
API_BASE_URL = settings.API_BASE_URL
logger.info(f"Conectando a la API en: {API_BASE_URL}")

@callback(
    Output("products-table", "data"), 
    Output("products-table-status", "children"), 
    Input("refresh-products-button", "n_clicks"), 
    prevent_initial_call=True 
)
def update_products_table(n_clicks: int) -> (list, str):
    """
    Callback para actualizar la tabla de productos al hacer clic
    en el boton de refrescar.
    """
    logger.info(f"Callback 'update_products_table' disparado por click {n_clicks}")
    
    try:
        api_url = f"{API_BASE_URL}/productos"
        logger.debug(f"Haciendo peticion GET a: {api_url}")
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            logger.debug("Productos obtenidos exitosamente de la API.")
            data = response.json()
            return data, f"Datos cargados. {len(data)} productos encontrados."
        else:
            logger.error(f"Error de la API: {response.status_code}")
            return no_update, f"Error al cargar datos: {response.status_code}"
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion a la API: {e}")
        return no_update, "Error: No se pudo conectar a la API. ¿Está el backend corriendo?"
    except Exception as e:
        logger.error(f"Error inesperado en callback: {e}", exc_info=True)
        return no_update, "Error inesperado."

@callback(
    Output("low-stock-table", "data"),
    Output("expiring-lotes-table", "data"),
    Output("low-stock-status", "children"),
    Output("expiring-lotes-status", "children"),
    Input("url", "pathname"), # Se dispara cuando la URL cambia
)
def update_alerts_dashboard(pathname: str) -> (list, list, str, str):
    """
    Callback para poblar el dashboard de alertas.
    Se dispara al cargar la pagina principal.
    """
    # Solo correr este callback si estamos en la pagina principal
    if pathname != "/":
        return no_update, no_update, no_update, no_update

    logger.info("Callback 'update_alerts_dashboard' disparado por carga de pagina.")
    
    # Estado inicial
    low_stock_data = []
    expiring_data = []
    low_stock_msg = ""
    expiring_msg = ""
    
    try:
        # 1. Obtener Alertas de Stock Mínimo
        low_stock_url = f"{API_BASE_URL}/alertas/stock-minimo"
        logger.debug(f"Haciendo peticion GET a: {low_stock_url}")
        low_stock_response = requests.get(low_stock_url)
        
        if low_stock_response.status_code == 200:
            low_stock_data = low_stock_response.json()
            low_stock_msg = f"Se encontraron {len(low_stock_data)} productos en alerta."
            logger.debug("Alertas de stock minimo obtenidas.")
        else:
            low_stock_msg = f"Error de API: {low_stock_response.status_code}"
            
        # 2. Obtener Alertas de Lotes por Vencer (30 dias)
        expiring_url = f"{API_BASE_URL}/alertas/por-vencer?days=30"
        logger.debug(f"Haciendo peticion GET a: {expiring_url}")
        expiring_response = requests.get(expiring_url)
        
        if expiring_response.status_code == 200:
            expiring_data = expiring_response.json()
            expiring_msg = f"Se encontraron {len(expiring_data)} lotes por vencer."
            logger.debug("Alertas de lotes por vencer obtenidas.")
        else:
            expiring_msg = f"Error de API: {expiring_response.status_code}"

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion a la API: {e}", exc_info=True)
        error_msg = "Error: No se pudo conectar a la API."
        return [], [], error_msg, error_msg
    except Exception as e:
        logger.error(f"Error inesperado en callback de alertas: {e}", exc_info=True)
        error_msg = "Error inesperado."
        return [], [], error_msg, error_msg

    return low_stock_data, expiring_data, low_stock_msg, expiring_msg
    
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname: str):
    """
    Callback de navegacion principal. Lee la URL y devuelve
    el layout de la pagina correspondiente.
    """
    logger.debug(f"Navegando a la pagina: {pathname}")
    
    # Importar el layout de alertas
    from layouts import products_layout, alerts_layout
    
    if pathname == "/productos":
        return products_layout
    elif pathname == "/inventario":
        # TODO: Crear el layout de inventario
        return html.P("Aquí va la gestión de inventario.")
    else:
        # La pagina principal (/) es el dashboard de alertas
        return alerts_layout # <-- Usar el layout real