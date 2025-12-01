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
    logger.info("Iniciando servidor de Dash en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)