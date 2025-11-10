# /----------------------------------------------------------------------------------\
# |  ID: DC-CFG-Dockerfile                                                           |
# |  Version: 3.0 (Regreso a pip/requirements.txt para robustez)                     |
# |  Descripcion: Define el contenedor de Docker para la aplicacion backend.           |
# \----------------------------------------------------------------------------------/

# --- Usar la version de Python de nuestra especificacion ---
FROM python:3.10-slim

# Establecer el directorio de trabajo DENTRO del contenedor
WORKDIR /app

# Actualizar pip y las herramientas de build ANTES de instalar
# Esto previene los errores de 'egg_info' y 'setup.py'
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar solo el archivo de requerimientos primero (buena practica de cache)
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de nuestra aplicacion
COPY ./backend /app/backend

# Establecer el directorio de trabajo a la carpeta 'backend'
WORKDIR /app/backend

# Exponer el puerto
EXPOSE 8000

# El comando para ejecutar la aplicacion
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]