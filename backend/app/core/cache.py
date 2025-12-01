# sistema-inventarios/backend/app/core/cache.py
from typing import Any, Optional, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryCache:
    """
    Sistema de cache simple en memoria (Singleton).
    Almacena resultados para evitar consultas costosas a la BD.
    """
    _instance = None
    _store: Dict[str, Any] = {}
    _expiry: Dict[str, datetime] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryCache, cls).__new__(cls)
            cls._store = {}
            cls._expiry = {}
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache si existe y no ha expirado."""
        if key in self._store:
            # Verificar expiracion si existe fecha limite
            if key in self._expiry:
                if datetime.now() > self._expiry[key]:
                    self.delete(key)
                    return None
            
            logger.debug(f"Cache HIT para: {key}")
            return self._store[key]
        
        logger.debug(f"Cache MISS para: {key}")
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Guarda un valor en el cache con un tiempo de vida (TTL)."""
        self._store[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
        logger.debug(f"Cache SET para: {key} (TTL: {ttl_seconds}s)")

    def delete(self, key: str) -> None:
        """Elimina una entrada especifica del cache."""
        if key in self._store:
            del self._store[key]
        if key in self._expiry:
            del self._expiry[key]
        logger.debug(f"Cache DELETE para: {key}")

    def invalidate_pattern(self, pattern: str) -> None:
        """
        Elimina claves que coincidan con un prefijo/patron simple.
        Util para invalidar grupos de cache (ej: 'alert_').
        """
        keys_to_delete = [k for k in self._store.keys() if k.startswith(pattern)]
        for k in keys_to_delete:
            self.delete(k)

# Instancia global para ser importada
cache = MemoryCache()
