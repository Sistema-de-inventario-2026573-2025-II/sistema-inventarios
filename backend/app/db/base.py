# sistema-inventarios/backend/app/db/base.py
from sqlalchemy.orm import declarative_base

# Base para todos los modelos ORM
Base = declarative_base()