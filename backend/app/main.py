# sistema-inventarios/backend/app/main.py
import logging
from fastapi import FastAPI
from app.api.api import api_router
from app.core.logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Aplicacion iniciada y logger configurado.")

app = FastAPI()

# Incluir el router principal
app.include_router(api_router, prefix="/api") # Prefijo global /api

# Endpoint de "hello world" para verificar que la app funciona
@app.get("/")
def read_root():
    return {"Hello": "World"}