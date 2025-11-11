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
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname: str):
    """
    Callback de navegacion principal. Lee la URL y devuelve
    el layout de la pagina correspondiente.
    """
    logger.debug(f"Navegando a la pagina: {pathname}")
    if pathname == "/productos":
        return products_layout
    elif pathname == "/inventario":
        # TODO: Crear el layout de inventario
        return html.P("Aquí va la gestión de inventario.")
    else:
        # La pagina principal (/) es el dashboard de alertas
        # TODO: Crear el layout de alertas
        return html.P("Aquí va el dashboard de alertas.")