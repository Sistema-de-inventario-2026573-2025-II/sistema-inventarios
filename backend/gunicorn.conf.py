import os

# Número de procesos de worker
workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))

# Número de hilos por worker
threads = int(os.environ.get('GUNICORN_THREADS', '4'))

# Host y puerto para enlazar
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

# Clase de worker de Uvicorn para FastAPI
worker_class = "uvicorn.workers.UvicornWorker"

# Nivel de log
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')

# Logs de acceso y error a stdout
accesslog = '-'
errorlog = '-'

# Tiempo máximo que un worker esperará por una respuesta (segundos)
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
