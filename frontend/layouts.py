from dash import html, dash_table
import dash_bootstrap_components as dbc
import logging

logger = logging.getLogger(__name__)

# Definir las columnas para nuestra tabla de productos
columnas_productos = [
    {"name": "ID", "id": "id"},
    {"name": "Nombre", "id": "nombre"},
    {"name": "SKU", "id": "sku"},
    {"name": "Precio", "id": "precio"},
    {"name": "Stock", "id": "cantidad_actual"},
    {"name": "Stock Min.", "id": "stock_minimo"},
]

# El layout principal de la seccion de productos
products_layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Gestión de Productos"), width=10),
        dbc.Col(
            dbc.Button(
                "Refrescar Datos", 
                id="refresh-products-button", # <-- ID para el callback
                color="primary"
            ),
            width=2,
            className="d-flex justify-content-end"
        )
    ], className="mb-3 align-items-center"),
    
    dbc.Row([
        dbc.Col([
            dbc.Alert("Cargando...", color="info", id="products-table-status"),
            dash_table.DataTable(
                id="products-table",
                columns=columnas_productos,
                data=[],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
            )
        ])
    ])
], fluid=True, className="p-3")

sidebar_layout = html.Div(
    [
        html.H2("Inventarios", className="display-4"),
        html.Hr(),
        html.P(
            "Un sistema de gestión TDD", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Alertas", href="/", active="exact"),
                dbc.NavLink("Productos", href="/productos", active="exact"),
                dbc.NavLink("Inventario", href="/inventario", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "backgroundColor": "#f8f9fa",
    },
)

content_layout = html.Div(
    id="page-content", 
    style={
        "marginLeft": "18rem",
        "marginRight": "2rem",
        "padding": "2rem 1rem",
    }
)