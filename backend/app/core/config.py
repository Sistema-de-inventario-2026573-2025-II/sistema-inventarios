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
    DATABASE_URL: str = "sqlite:///./default.db"

@lru_cache()
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings."""
    return Settings()