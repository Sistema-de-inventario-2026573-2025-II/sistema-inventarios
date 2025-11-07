# sistema-inventarios/backend/app/db/init_db.py

import sys
from pathlib import Path


script_path = Path(__file__).resolve()
backend_root = script_path.parent.parent.parent
sys.path.append(str(backend_root))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base

import app.models


def init_db(db: Session) -> None:
    """
    Inicializa la base de datos, creando las tablas.
    """
    # Base.metadata.create_all() es idempotente,
    # no recreara tablas que ya existen.
    Base.metadata.create_all(bind=engine)
    print(engine.url)
    

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