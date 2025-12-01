# sistema-inventarios/frontend/app.py
import dash
import logging
import callbacks 
from dashboard import app
from dash import html, dcc
import dash_bootstrap_components as dbc # Nueva importacion
from layouts import sidebar_layout, content_layout # Re-agregar importaciones

logger = logging.getLogger(__name__)

# Definir los temas que usaremos
THEMES = {
    "light": dbc.themes.BOOTSTRAP,
    "dark": dbc.themes.DARKLY,
}

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