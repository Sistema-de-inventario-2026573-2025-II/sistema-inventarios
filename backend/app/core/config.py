# sistema-inventarios/backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Gestiona la configuracion de la aplicacion usando variables de entorno.
    """
    # Lee el .env file ubicado en la carpeta 'backend'
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')

    DATABASE_URL: str = "sqlite:///./default.db"

@lru_cache()
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings."""
    return Settings()