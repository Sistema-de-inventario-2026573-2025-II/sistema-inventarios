# sistema-inventarios/frontend/dashboard.py
import dash
from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    # Requerido para que los callbacks en otros archivos funcionen
    suppress_callback_exceptions=True
)