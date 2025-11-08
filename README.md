# Sistema de Inventarios

Este proyecto implementa un sistema de inventarios básico utilizando FastAPI para el backend y SQLite como base de datos. Permite gestionar productos, lotes y movimientos de inventario.

## Características

*   **API RESTful:** Interfaz bien definida para la gestión de inventarios.
*   **Base de Datos SQLite:** Ligera y fácil de configurar para desarrollo.
*   **Validación de Datos:** Utiliza Pydantic para asegurar la integridad de los datos.
*   **Documentación Interactiva:** Generada automáticamente con Swagger UI (disponible en `/docs`).
*   **Pruebas Unitarias:** Cobertura de pruebas para asegurar la funcionalidad.

## Estructura del Proyecto
sistema-inventarios/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── batches.py
│   │   │   │   ├── products.py
│   │   │   │   └── movements.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── base_class.py
│   │   │   ├── init_db.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── batch.py
│   │   │   ├── movement.py
│   │   │   ├── product.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── batch.py
│   │   │   ├── movement.py
│   │   │   ├── product.py
│   │   │   └── __init__.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── tests/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── test_batches.py
│   │   │   │   ├── test_products.py
│   │   │   │   └── test_movements.py
│   │   │   └── __init__.py
│   │   ├── conftest.py
│   │   └── __init__.py
│   ├── .env.example
│   └── inventario.db (generado al inicializar la DB)
├── .gitignore
├── README.md
├── setup.md
└── pyproject.toml
## Configuración y Ejecución

Para configurar el entorno de desarrollo y ejecutar la aplicación, sigue las instrucciones detalladas en [setup.md](setup.md).