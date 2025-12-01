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
        html.Div(
            [
                dbc.Label("Modo Oscuro", html_for="theme-toggle-switch"),
                dbc.Switch(
                    id="theme-toggle-switch",
                    value=False,  # Por defecto: tema claro
                    className="ms-2",
                ),
            ],
            className="d-flex align-items-center mb-3"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Alertas", href="/", active="exact"),
                dbc.NavLink("Productos", href="/productos", active="exact"),
                dbc.NavLink("Inventario", href="/inventario", active="exact"),
                dbc.NavLink("Reportes", href="/reportes", active="exact"), # Nuevo enlace
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
    {"name": "ID Alerta", "id": "id"},
    {"name": "Producto", "id": "producto_nombre"},
    {"name": "SKU", "id": "sku"},
    {"name": "Stock Actual", "id": "cantidad_actual"},
    {"name": "Stock Mínimo", "id": "stock_minimo"},
    {"name": "Mensaje", "id": "mensaje"},
]

columnas_por_vencer = [
    {"name": "ID Alerta", "id": "id"},
    {"name": "Lote ID", "id": "entidad_id"},
    {"name": "Producto", "id": "producto_nombre"},
    {"name": "SKU", "id": "producto_sku"},
    {"name": "Cantidad Lote", "id": "cantidad_actual"},
    {"name": "Fecha Venc.", "id": "fecha_vencimiento"},
    {"name": "Mensaje", "id": "mensaje"},
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

# Definir columnas para nuestra tabla de lotes
columnas_lotes = [
    {"name": "ID", "id": "id"},
    {"name": "Producto SKU", "id": "producto_sku"},
    {"name": "Cantidad Recibida", "id": "cantidad_recibida"},
    {"name": "Cantidad Actual", "id": "cantidad_actual"},
    {"name": "Fecha Vencimiento", "id": "fecha_vencimiento"},
]

# Definir columnas para el reporte de inventario basico
columnas_reporte_inventario_basico = [
    {"name": "ID", "id": "id"},
    {"name": "Nombre", "id": "nombre"},
    {"name": "SKU", "id": "sku"},
    {"name": "Precio", "id": "precio"},
    {"name": "Stock Actual", "id": "cantidad_actual"},
    {"name": "Stock Mínimo", "id": "stock_minimo"},
]

inventory_layout = dbc.Container([
    html.H2("Gestión de Inventario"),
    html.Hr(),

    # Sección para Registrar Entradas (Lotes)
    dbc.Row([
        dbc.Col([
            html.H4("Registrar Entrada de Lote"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Producto", width=2),
                    dbc.Col(dcc.Dropdown(
                        id="entry-product-dropdown",
                        options=[], # Options will be populated by callback
                        placeholder="Seleccione un producto",
                    ), width=10),
                ], className="mb-3"),
                # Campo oculto para almacenar el product_id real
                dcc.Input(id="entry-product-id", type="hidden", value=None),
                dbc.Row([
                    dbc.Label("Cantidad", width=2),
                    dbc.Col(dbc.Input(type="number", id="entry-quantity", placeholder="Cantidad a ingresar"), width=10),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Fecha Venc.", width=2),
                    dbc.Col(dcc.DatePickerSingle(id="entry-expiration-date", placeholder="Fecha de vencimiento"), width=10),
                ], className="mb-3"),
            ]),
            dbc.Button("Registrar Entrada", id="register-entry-button", color="primary"),
            dbc.Alert("...", id="entry-result-status", color="info", className="mt-3"),
        ])
    ], className="mb-5"),

    # Sección para Registrar Salidas (Despachos)
    dbc.Row([
        # Columna para Despacho Simple (por Lote ID)
        dbc.Col([
            html.H4("Registrar Salida Simple (por Lote)"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Lote ID", width=2),
                    dbc.Col(dbc.Input(type="number", id="dispatch-lote-id", placeholder="ID del lote a despachar"), width=10),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Cantidad", width=2),
                    dbc.Col(dbc.Input(type="number", id="dispatch-lote-quantity", placeholder="Cantidad a despachar"), width=10),
                ], className="mb-3"),
            ]),
            dbc.Button("Registrar Salida", id="register-dispatch-lote-button", color="warning"),
            dbc.Alert("...", id="dispatch-lote-result-status", color="info", className="mt-3"),
        ], width=6),

        # Columna para Despacho FEFO (Inteligente)
        dbc.Col([
            html.H4("Registrar Salida FEFO (Automático)"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Producto", width=2),
                    dbc.Col(dcc.Dropdown(
                        id="dispatch-fefo-product-dropdown",
                        options=[], # Options will be populated by callback
                        placeholder="Seleccione un producto",
                    ), width=10),
                ], className="mb-3"),
                # Campo oculto para almacenar el product_id real
                dcc.Input(id="dispatch-fefo-product-id", type="hidden", value=None),
                dbc.Row([
                    dbc.Label("Cantidad", width=2),
                    dbc.Col(dbc.Input(type="number", id="dispatch-fefo-quantity", placeholder="Cantidad a despachar"), width=10),
                ], className="mb-3"),
            ]),
            dbc.Button("Despachar FEFO", id="dispatch-fefo-button", color="danger"),
            dbc.Alert("...", id="dispatch-fefo-result-status", color="info", className="mt-3"),
        ], width=6),
    ]),

    html.Hr(className="my-5"), # Separador

    # Sección para Mostrar Lotes Existentes
    dbc.Row([
        dbc.Col([
            html.H3("Lotes Existentes"),
            dcc.Interval(id="lotes-interval", interval=60*1000, n_intervals=0), # Auto-refresh
            dbc.Button(
                "Refrescar Lotes",
                id="refresh-lotes-button", # Boton de refresco manual
                color="info",
                className="mb-3"
            ),
            dbc.Alert("Cargando lotes...", color="info", id="lotes-table-status"),
            dash_table.DataTable(
                id="lotes-table",
                columns=columnas_lotes,
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