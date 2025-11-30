from dash import html, dcc, dash_table
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
    dcc.Interval(id="products-interval", interval=60*1000, n_intervals=0),
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

# Definir columnas para las tablas de alertas
columnas_stock_bajo = [
    {"name": "SKU", "id": "sku"},
    {"name": "Nombre", "id": "nombre"},
    {"name": "Stock Actual", "id": "cantidad_actual"},
    {"name": "Stock Mínimo", "id": "stock_minimo"},
]

columnas_por_vencer = [
    {"name": "Lote ID", "id": "id"},
    {"name": "Producto SKU", "id": "producto_sku"}, # Asumimos que el API lo dara
    {"name": "Stock Lote", "id": "cantidad_actual"},
    {"name": "Fecha Venc.", "id": "fecha_vencimiento"},
]

alerts_layout = dbc.Container([
    # Trigger para el callback (se dispara al cargar la pagina)
    dcc.Location(id="alerts-url-trigger", refresh=True),
    
    dbc.Row(html.H2("Dashboard de Alertas")),
    html.Hr(),
    
    # Fila para Alerta de Stock Bajo
    dbc.Row([
        dbc.Col([
            html.H4("Alerta: Stock Mínimo"),
            dbc.Alert(
                "Cargando...", 
                color="info", 
                id="low-stock-status" # ID para el callback
            ),
            dash_table.DataTable(
                id="low-stock-table", # ID para el callback
                columns=columnas_stock_bajo,
                data=[],
                page_size=5,
                style_table={'overflowX': 'auto'},
            )
        ])
    ], className="mb-4"),
    
    # Fila para Alerta de Lotes por Vencer
    dbc.Row([
        dbc.Col([
            html.H4("Alerta: Lotes Próximos a Vencer (30 días)"),
            dbc.Alert(
                "Cargando...", 
                color="info", 
                id="expiring-lotes-status" # ID para el callback
            ),
            dash_table.DataTable(
                id="expiring-lotes-table", # ID para el callback
                columns=columnas_por_vencer,
                data=[],
                page_size=5,
                style_table={'overflowX': 'auto'},
            )
        ])
    ])
], fluid=True, className="p-3")