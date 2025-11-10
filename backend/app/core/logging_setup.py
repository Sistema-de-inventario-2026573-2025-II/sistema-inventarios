# sistema-inventarios/backend/app/core/logging_setup.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()

# Colocar el archivo de log en la carpeta 'backend'
LOG_FILE = Path(__file__).resolve().parent.parent.parent / "inventario.log"

# Formato de consola (con color)
CONSOLE_LOG_FORMAT = (
    "  %(log_color)s%(levelname)-8s%(reset)s | "
    "%(log_color)s%(name)-12s%(reset)s | "  # <-- %(name)s anadido
    "%(log_color)s%(message)s%(reset)s"
)

# Formato de archivo (detallado)
FILE_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging():
    """Configures the root logger for the application."""
    logger = logging.getLogger()

    # Mapear el string del nivel a un logging constant
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(logging.DEBUG)  # <-- Nivel mas bajo en el root

    # Prevenir duplicados si se llama accidentalmente de nuevo
    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return logger

    # 1. Handler para la Consola (Stream)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(ColoredFormatter(CONSOLE_LOG_FORMAT))
    stream_handler.setLevel(level)  # <-- Nivel de consola (e.g., INFO)
    logger.addHandler(stream_handler)

    # 2. Handler para el Archivo (Rotativo)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1048576, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
    file_handler.setLevel(logging.DEBUG)  # <-- Nivel de archivo (DEBUG)
    logger.addHandler(file_handler)
    
    if settings.LOG_LEVEL.upper() != "DEBUG":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger