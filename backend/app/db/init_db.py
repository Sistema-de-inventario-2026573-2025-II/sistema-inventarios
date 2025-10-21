# sistema-inventarios/backend/app/db/init_db.py

import sys
from pathlib import Path


script_path = Path(__file__).resolve()
backend_root = script_path.parent.parent.parent
sys.path.append(str(backend_root))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base

# --- Importar todos los modelos ---
# Esto es crucial para que Base.metadata los reconozca
from app.models.producto import Producto
# (Cuando agreguemos mas modelos, los importaremos aqui)

def init_db(db: Session) -> None:
    """
    Inicializa la base de datos, creando las tablas.
    """
    # Base.metadata.create_all() es idempotente,
    # no recreara tablas que ya existen.
    Base.metadata.create_all(bind=engine)

def main() -> None:
    """
Imprimira un mensaje indicando que la base de datos
    se esta inicializando.
    """
    print("Inicializando la base de datos...")
    try:
        db = SessionLocal()
        init_db(db)
        print("Base de datos inicializada exitosamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()