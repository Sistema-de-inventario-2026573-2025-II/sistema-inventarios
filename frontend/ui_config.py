import os
from functools import lru_cache
import logging
import dash_bootstrap_components as dbc # Nueva importacion

logger = logging.getLogger(__name__)

# Definir los temas que usaremos
THEMES = {
    "light": dbc.themes.BOOTSTRAP,
    "dark": dbc.themes.DARKLY,
}

class FrontendSettings:
    """
    Gestiona la configuracion del frontend, leyendo de variables de entorno.
    """
    # Valor por defecto para desarrollo (corriendo ambos localmente)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

@lru_cache()
def get_frontend_settings() -> FrontendSettings:
    """Retorna una instancia cacheada de FrontendSettings."""
    logger.debug("Cargando configuracion del frontend...")
    return FrontendSettings()