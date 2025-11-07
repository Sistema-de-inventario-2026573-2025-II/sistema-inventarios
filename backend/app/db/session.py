# sistema-inventarios/backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

script_path = Path(__file__).resolve()
backend_root = script_path.parent.parent.parent
sys.path.append(str(backend_root))
from app.core.config import get_settings

settings = get_settings()

# 'check_same_thread' es solo para SQLite.
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    print(engine.url)