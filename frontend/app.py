# sistema-inventarios/frontend/app.py
import dash
import logging
import callbacks 
from dashboard import app
from dash import html, dcc
from layouts import sidebar_layout, content_layout

logger = logging.getLogger(__name__)

# Este es el layout principal de nuestra App
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar_layout,
    content_layout
])

# --- Entrypoint para Correr el Servidor ---
if __name__ == '__main__':
    logger.info("Iniciando servidor de Dash en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)