# sistema-inventarios/backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# 1. Encontrar la ruta al directorio 'backend'
# __file__ es .../backend/app/core/config.py
# .parent.parent.parent es .../backend
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

# 2. Construir la ruta al archivo .env
ENV_PATH = BACKEND_ROOT / ".env"

class Settings(BaseSettings):
    """
    Gestiona la configuracion de la aplicacion usando variables de entorno.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8'
    )
    
    # Configuracion para la base de datos de produccion (PostgreSQL)
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: int = 5432
    
    # URL de base de datos (se construye dinamicamente)
    # Si no se proveen las variables de entorno de Postgres,
    # se usara una base de datos SQLite por defecto.
    DATABASE_URL: str | None = None

    LOG_LEVEL: str = "INFO"

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de Settings.
    Construye la URL de la BD si no esta definida.
    """
    settings = Settings()
    
    # Si no se ha definido una URL de BD, la construimos
    if settings.DATABASE_URL is None:
        # Usar PostgreSQL si las variables estan disponibles
        if all([
            settings.POSTGRES_USER, 
            settings.POSTGRES_PASSWORD,
            settings.POSTGRES_SERVER,
            settings.POSTGRES_DB
        ]):
            settings.DATABASE_URL = (
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
                f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
        # Si no, usar SQLite como fallback para desarrollo
        else:
            settings.DATABASE_URL = "sqlite:///./default.db"

    return settings