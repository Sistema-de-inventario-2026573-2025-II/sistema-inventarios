# sistema-inventarios/frontend/app.py
import dash
import logging
import callbacks 
from dashboard import app
from dash import html, dcc
import dash_bootstrap_components as dbc # Nueva importacion
from layouts import sidebar_layout, content_layout # Re-agregar importaciones
from ui_config import THEMES # Importar THEMES desde ui_config

logger = logging.getLogger(__name__)

# Este es el layout principal de nuestra App
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id='theme-store', data={'theme': 'light'}), # Almacenar el tema actual
    html.Link(id='stylesheet-link', rel='stylesheet', href=THEMES['light']), # Enlace CSS dinámico
    sidebar_layout,
    content_layout
])

# --- Entrypoint para Correr el Servidor ---
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8050))
    logger.info(f"Iniciando servidor de Dash en http://0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)