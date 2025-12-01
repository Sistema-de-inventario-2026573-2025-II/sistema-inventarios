import logging
import requests
import dash
from dash import callback, Output, Input, State, no_update, html
from typing import List
from ui_config import get_frontend_settings
from frontend.app import THEMES # Importar THEMES desde app.py (correccion de importacion absoluta)

logger = logging.getLogger(__name__)

settings = get_frontend_settings()
API_BASE_URL = settings.API_BASE_URL
logger.info(f"Conectando a la API en: {API_BASE_URL}")

@callback(
    Output("theme-store", "data"),
    Output("stylesheet-link", "href"),
    Input("theme-toggle-switch", "value"),
    prevent_initial_call=False
)
def toggle_theme(is_dark_mode_on: bool) -> tuple[dict, str]:
    """
    Callback para cambiar el tema de la aplicacion entre claro y oscuro.
    Actualiza dcc.Store y el href del stylesheet.
    """
    ctx = dash.callback_context
    # Si el callback se dispara en la carga inicial, no cambiamos el tema
    # Esto es para evitar un cambio de tema no deseado al cargar la pagina
    if not ctx.triggered:
        return {"theme": "light"}, THEMES["light"]
        
    new_theme_key = "dark" if is_dark_mode_on else "light"
    new_theme_url = THEMES[new_theme_key]
    logger.info(f"Cambiando tema a: {new_theme_key}")
    return {"theme": new_theme_key}, new_theme_url

@callback(
    Output("products-table", "data"), 
    Output("products-table-status", "children"), 
    Input("refresh-products-button", "n_clicks"),
    Input("products-interval", "n_intervals")
)
def update_products_table(n_clicks: int, n_intervals: int) -> tuple[list, str]:
    """
    Callback para actualizar la tabla de productos al hacer clic
    en el boton de refrescar O por el intervalo automatico.
    """
    trigger_id = "unknown"
    ctx = dash.callback_context
    if not ctx.triggered:
        logger.warning("Callback 'update_products_table' disparado sin trigger conocido.")
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    logger.info(
        f"Callback 'update_products_table' disparado por: {trigger_id} "
        f"(clicks={n_clicks}, intervals={n_intervals})"
    )
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
def update_alerts_dashboard(pathname: str) -> tuple[list, list, str, str]:
    """
    Callback para poblar el dashboard de alertas.
    Se dispara al cargar la pagina principal.
    """
    # Solo correr este callback si estamos en la pagina principal
    if pathname != "/":
        return no_update, no_update, no_update, no_update

    logger.info("Callback 'update_alerts_dashboard' disparado por carga de pagina.")
    
    # Estado inicial
    processed_low_stock_data = []
    processed_expiring_data = []
    low_stock_msg = ""
    expiring_msg = ""
    
    try:
        # 1. Obtener Alertas de Stock Mínimo
        low_stock_url = f"{API_BASE_URL}/alertas/stock-minimo"
        logger.debug(f"Haciendo peticion GET a: {low_stock_url}")
        low_stock_response = requests.get(low_stock_url)
        
        if low_stock_response.status_code == 200:
            alerts_data = low_stock_response.json()
            processed_low_stock_data = _process_low_stock_alerts(alerts_data)
            low_stock_msg = f"Se encontraron {len(processed_low_stock_data)} alertas de stock mínimo."
            logger.debug("Alertas de stock minimo obtenidas y procesadas.")
        else:
            low_stock_msg = f"Error de API al obtener stock mínimo: {low_stock_response.status_code}"
            logger.error(low_stock_msg)
            
        # 2. Obtener Alertas de Lotes por Vencer (30 dias)
        expiring_url = f"{API_BASE_URL}/alertas/por-vencer?days=30"
        logger.debug(f"Haciendo peticion GET a: {expiring_url}")
        expiring_response = requests.get(expiring_url)
        
        if expiring_response.status_code == 200:
            alerts_data = expiring_response.json()
            processed_expiring_data = _process_expiring_lotes_alerts(alerts_data)
            expiring_msg = f"Se encontraron {len(processed_expiring_data)} alertas de lotes por vencer."
            logger.debug("Alertas de lotes por vencer obtenidas y procesadas.")
        else:
            expiring_msg = f"Error de API al obtener lotes por vencer: {expiring_response.status_code}"
            logger.error(expiring_msg)

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion a la API: {e}", exc_info=True)
        error_msg = "Error: No se pudo conectar a la API. ¿Está el backend corriendo?"
        return [], [], error_msg, error_msg
    except Exception as e:
        logger.error(f"Error inesperado en callback de alertas: {e}", exc_info=True)
        error_msg = "Error inesperado."
        return [], [], error_msg, error_msg

    return processed_low_stock_data, processed_expiring_data, low_stock_msg, expiring_msg

def _process_low_stock_alerts(alerts: List[dict]) -> List[dict]:
    """Procesa alertas de stock mínimo para visualización en tabla."""
    processed_data = []
    for alert in alerts:
        metadata = alert.get("metadata_json", {})
        processed_data.append({
            "id": alert["id"],
            "producto_nombre": metadata.get("nombre", "N/A"),
            "sku": metadata.get("sku", "N/A"),
            "cantidad_actual": metadata.get("cantidad_actual", "N/A"),
            "stock_minimo": metadata.get("stock_minimo", "N/A"),
            "mensaje": alert.get("mensaje", "N/A"),
        })
    return processed_data

def _process_expiring_lotes_alerts(alerts: List[dict]) -> List[dict]:
    """Procesa alertas de lotes por vencer para visualización en tabla."""
    processed_data = []
    for alert in alerts:
        metadata = alert.get("metadata_json", {})
        processed_data.append({
            "id": alert["id"],
            "entidad_id": alert["entidad_id"], # El lote ID es la entidad_id
            "producto_nombre": metadata.get("producto_nombre", "N/A"),
            "producto_sku": metadata.get("producto_sku", "N/A"),
            "cantidad_actual": metadata.get("cantidad_actual", "N/A"),
            "fecha_vencimiento": metadata.get("fecha_vencimiento", "N/A"),
            "mensaje": alert.get("mensaje", "N/A"),
        })
    return processed_data

    
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
    
    # Import layouts inside the callback to prevent circular dependencies
    from layouts import alerts_layout, products_layout, inventory_layout
    
    if pathname == "/productos":
        return products_layout
    elif pathname == "/inventario":
        return inventory_layout
    else:
        # La pagina principal (/) es el dashboard de alertas
        return alerts_layout # <-- Usar el layout real

@callback(
    Output("entry-product-dropdown", "options"),
    Output("entry-product-dropdown", "value"), # Para limpiar la seleccion
    Input("url", "pathname"), # Se dispara cuando la URL cambia (ej. al ir a la pagina de inventario)
    Input("register-entry-button", "n_clicks") # Para refrescar despues de una entrada
)
def update_product_dropdown_options(pathname: str, n_clicks: int) -> tuple[list, None]:
    """
    Callback para cargar las opciones del dropdown de productos.
    Se dispara al cargar la pagina de inventario o despues de registrar una entrada.
    """
    ctx = dash.callback_context
    if not ctx.triggered or (ctx.triggered[0]['prop_id'] == 'url.pathname' and pathname != "/inventario"):
        return no_update, no_update
        
    logger.info("Cargando opciones para dropdown de productos.")
    try:
        api_url = f"{API_BASE_URL}/productos"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            productos = response.json()
            options = [{"label": f"{p['nombre']} (SKU: {p['sku']})", "value": p['id']} for p in productos]
            return options, None # Limpiar la seleccion actual
        else:
            logger.error(f"Error al cargar productos para dropdown: {response.status_code}")
            return no_update, no_update
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion al cargar productos para dropdown: {e}")
        return no_update, no_update
    except Exception as e:
        logger.error(f"Error inesperado al cargar productos para dropdown: {e}", exc_info=True)
        return no_update, no_update

@callback(
    Output("entry-product-id", "value"), # Actualizar el campo oculto con el ID seleccionado
    Input("entry-product-dropdown", "value"),
)
def update_selected_product_id(selected_value: int) -> int:
    """
    Actualiza el campo oculto 'entry-product-id' con el valor seleccionado del dropdown.
    """
    return selected_value

@callback(
    Output("entry-result-status", "children"),
    Output("entry-result-status", "color"),
    Input("register-entry-button", "n_clicks"),
    State("entry-product-id", "value"), # Ahora se toma del campo oculto
    State("entry-quantity", "value"),
    State("entry-expiration-date", "date"),
    prevent_initial_call=True
)
def register_inventory_entry(n_clicks, product_id, quantity, expiration_date):
    """
    Callback para registrar una nueva entrada de inventario (lote).
    """
    logger.info(f"Callback 'register_inventory_entry' disparado. Clicks: {n_clicks}")

    if not all([product_id, quantity, expiration_date]):
        logger.warning("Faltan datos en el formulario de registro de entrada.")
        return "Todos los campos son obligatorios.", "warning"

    try:
        api_url = f"{API_BASE_URL}/inventario/entradas"
        payload = {
            "producto_id": product_id,
            "cantidad_recibida": quantity,
            "fecha_vencimiento": expiration_date,
        }
        logger.debug(f"Haciendo peticion POST a: {api_url} con payload: {payload}")
        
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 201:
            lote = response.json()
            msg = f"Lote registrado con éxito. ID del Lote: {lote['id']}"
            logger.info(msg)
            return msg, "success"
        else:
            error_msg = f"Error de la API ({response.status_code}): {response.text}"
            logger.error(error_msg)
            return error_msg, "danger"
            
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Error de conexión a la API: {e}"
        logger.error(error_msg, exc_info=True)
        return "Error: No se pudo conectar a la API.", "danger"
    except Exception as e:
        error_msg = f"Error inesperado en callback: {e}"
        logger.error(error_msg, exc_info=True)
        return "Error inesperado en el servidor.", "danger"
        
@callback(
    Output("dispatch-lote-result-status", "children"),
    Output("dispatch-lote-result-status", "color"),
    Input("register-dispatch-lote-button", "n_clicks"),
    State("dispatch-lote-id", "value"),
    State("dispatch-lote-quantity", "value"),
    prevent_initial_call=True
)
def register_simple_dispatch(n_clicks, lote_id, quantity):
    """
    Callback para registrar una salida de inventario por ID de lote.
    """
    logger.info(f"Callback 'register_simple_dispatch' disparado. Clicks: {n_clicks}")

    if not all([lote_id, quantity]):
        return "ID de Lote y Cantidad son obligatorios.", "warning"

    try:
        api_url = f"{API_BASE_URL}/inventario/salidas"
        payload = {"lote_id": lote_id, "cantidad": quantity}
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 201:
            msg = "Salida registrada con éxito."
            logger.info(msg)
            return msg, "success"
        else:
            return f"Error de la API ({response.status_code}): {response.text}", "danger"

    except requests.exceptions.ConnectionError as e:
        return "Error: No se pudo conectar a la API.", "danger"
    except Exception as e:
        return f"Error inesperado: {e}", "danger"

@callback(
    Output("dispatch-fefo-result-status", "children"),
    Output("dispatch-fefo-result-status", "color"),
    Input("dispatch-fefo-button", "n_clicks"),
    State("dispatch-fefo-product-id", "value"),
    State("dispatch-fefo-quantity", "value"),
    prevent_initial_call=True
)
def register_fefo_dispatch(n_clicks, product_id, quantity):
    """
    Callback para registrar una salida de inventario usando la estrategia FEFO.
    """
    logger.info(f"Callback 'register_fefo_dispatch' disparado. Clicks: {n_clicks}")

    if not all([product_id, quantity]):
        return "ID de Producto y Cantidad son obligatorios.", "warning"

    try:
        api_url = f"{API_BASE_URL}/inventario/despachar"
        payload = {"producto_id": product_id, "cantidad": quantity}
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            msg = "Salida FEFO registrada con éxito."
            logger.info(msg)
            return msg, "success"
        else:
            return f"Error de la API ({response.status_code}): {response.text}", "danger"

    except requests.exceptions.ConnectionError as e:
        return "Error: No se pudo conectar a la API.", "danger"
    except Exception as e:
        return f"Error inesperado: {e}", "danger"

@callback(
    Output("lotes-table", "data"),
    Output("lotes-table-status", "children"),
    Input("refresh-lotes-button", "n_clicks"),
    Input("lotes-interval", "n_intervals")
)
def update_lotes_table(n_clicks: int, n_intervals: int) -> tuple[list, str]:
    """
    Callback para actualizar la tabla de lotes al hacer clic
    en el boton de refrescar O por el intervalo automatico.
    """
    trigger_id = "unknown"
    ctx = dash.callback_context
    if not ctx.triggered:
        logger.warning("Callback 'update_lotes_table' disparado sin trigger conocido.")
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    logger.info(
        f"Callback 'update_lotes_table' disparado por: {trigger_id} "
        f"(clicks={n_clicks}, intervals={n_intervals})"
    )
    try:
        api_url = f"{API_BASE_URL}/lotes"
        logger.debug(f"Haciendo peticion GET a: {api_url}")
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            logger.debug("Lotes obtenidos exitosamente de la API.")
            lotes_raw_data = response.json()
            
            # Procesar datos para incluir el SKU del producto
            lotes_processed_data = []
            for lote in lotes_raw_data:
                processed_lote = lote.copy()
                if "producto" in lote and "sku" in lote["producto"]:
                    processed_lote["producto_sku"] = lote["producto"]["sku"]
                else:
                    processed_lote["producto_sku"] = "N/A" # O manejar de otra forma
                lotes_processed_data.append(processed_lote)

            return lotes_processed_data, f"Datos cargados. {len(lotes_processed_data)} lotes encontrados."
        else:
            logger.error(f"Error de la API al cargar lotes: {response.status_code}")
            return no_update, f"Error al cargar lotes: {response.status_code}"
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion a la API al cargar lotes: {e}")
        return no_update, "Error: No se pudo conectar a la API. ¿Está el backend corriendo?"
    except Exception as e:
        logger.error(f"Error inesperado en callback 'update_lotes_table': {e}", exc_info=True)
        return no_update, "Error inesperado."

@callback(
    Output("dispatch-fefo-product-dropdown", "options"),
    Output("dispatch-fefo-product-dropdown", "value"), # Para limpiar la seleccion
    Input("url", "pathname"), # Se dispara cuando la URL cambia (ej. al ir a la pagina de inventario)
    Input("dispatch-fefo-button", "n_clicks") # Para refrescar despues de un despacho
)
def update_fefo_product_dropdown_options(pathname: str, n_clicks: int) -> tuple[list, None]:
    """
    Callback para cargar las opciones del dropdown de productos para despacho FEFO.
    Se dispara al cargar la pagina de inventario o despues de registrar un despacho.
    """
    ctx = dash.callback_context
    if not ctx.triggered or (ctx.triggered[0]['prop_id'] == 'url.pathname' and pathname != "/inventario"):
        return no_update, no_update
        
    logger.info("Cargando opciones para dropdown de productos para despacho FEFO.")
    try:
        api_url = f"{API_BASE_URL}/productos"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            productos = response.json()
            options = [{"label": f"{p['nombre']} (SKU: {p['sku']})", "value": p['id']} for p in productos]
            return options, None # Limpiar la seleccion actual
        else:
            logger.error(f"Error al cargar productos para dropdown FEFO: {response.status_code}")
            return no_update, no_update
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexion al cargar productos para dropdown FEFO: {e}")
        return no_update, no_update
    except Exception as e:
        logger.error(f"Error inesperado al cargar productos para dropdown FEFO: {e}", exc_info=True)
        return no_update, no_update

@callback(
    Output("dispatch-fefo-product-id", "value"), # Actualizar el campo oculto con el ID seleccionado
    Input("dispatch-fefo-product-dropdown", "value"),
)
def update_fefo_selected_product_id(selected_value: int) -> int:
    """
    Actualiza el campo oculto 'dispatch-fefo-product-id' con el valor seleccionado del dropdown.
    """
    return selected_value

@callback(
    Output("dispatch-fefo-result-status", "children"),
    Output("dispatch-fefo-result-status", "color"),
    Input("dispatch-fefo-button", "n_clicks"),
    State("dispatch-fefo-product-id", "value"), # Ahora se toma del campo oculto
    State("dispatch-fefo-quantity", "value"),
    prevent_initial_call=True
)
def register_fefo_dispatch(n_clicks, product_id, quantity):
    """
    Callback para registrar una salida de inventario usando la estrategia FEFO.
    """
    logger.info(f"Callback 'register_fefo_dispatch' disparado. Clicks: {n_clicks}")

    if not all([product_id, quantity]):
        return "ID de Producto y Cantidad son obligatorios.", "warning"

    try:
        api_url = f"{API_BASE_URL}/inventario/despachar"
        payload = {"producto_id": product_id, "cantidad": quantity}
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            msg = "Salida FEFO registrada con éxito."
            logger.info(msg)
            return msg, "success"
        else:
            return f"Error de la API ({response.status_code}): {response.text}", "danger"

    except requests.exceptions.ConnectionError as e:
        return "Error: No se pudo conectar a la API.", "danger"
    except Exception as e:
        return f"Error inesperado: {e}", "danger"
