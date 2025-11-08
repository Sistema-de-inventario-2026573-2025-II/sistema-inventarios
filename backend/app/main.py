# sistema-inventarios/backend/app/main.py
from fastapi import FastAPI
from app.api.api import api_router  # <-- Importar el router

app = FastAPI()

# Incluir el router principal
app.include_router(api_router, prefix="/api") # Prefijo global /api

# Endpoint de "hello world" para verificar que la app funciona
@app.get("/")
def read_root():
    return {"Hello": "World"}