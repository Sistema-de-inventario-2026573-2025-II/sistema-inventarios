# **🚀 Guía de Configuración del Entorno de Desarrollo**

Esta guía te llevará desde cero hasta tener un servidor de desarrollo funcional para el Sistema de Inventarios.

### **Paso 1: Prerrequisitos (Python y uv)**

Necesitarás python (versión 3.10 o superior) y uv (nuestro gestor de paquetes).

**1\. Instalar Python (3.10+):**

* **Verifica si ya lo tienes:**  
  ```
  python3 \--version
  ```

* Si no lo tienes o la versión es anterior a 3.10, descárgalo e instálalo desde python.org.

**2\. Instalar uv:**

* uv es un gestor de paquetes y entornos virtuales ultrarrápido que reemplaza a pip y venv.  
* Abre tu terminal y ejecuta el comando correspondiente a tu sistema operativo.  
  * **En macOS o Linux:**  
   ``` bash
   curl \-LsSf \[https://astral.sh/uv/install.sh\](https://astral.sh/uv/install.sh) | sh
   ```

  * **En Windows (usando PowerShell):**  
   ```
    powershell \-c "irm \[https://astral.sh/uv/install.ps1\](https://astral.sh/uv/install.ps1) | iex"
   ```
* Cierra y reabre tu terminal para asegurarte de que uv esté en tu PATH.

### **Paso 2: Obtener el Proyecto**

1. **Clona el repositorio:**  
   * Navega a la carpeta donde guardas tus proyectos y ejecuta git clone. (Reemplaza la URL por la de tu repositorio).  
     ```
     git clone https://github.com/Sistema-de-inventario-2026573-2025-II/sistema-inventarios.git
     ```

2. **Entra a la carpeta del proyecto:**  
   ``` bash
   cd sistema-inventarios
   ```

### **Paso 3: Configuración del Entorno Virtual**

1. **Crea el Entorno Virtual:**  
   * Usa uv para configurar un entorno virtual local llamado .venv.  
     ``` bash
     uv sync
     ```

2. **Activa el Entorno:**  
   * Debes "activar" el entorno para usarlo en tu sesión de terminal.  
   * **En macOS o Linux:**  
     ``` bash
     source .venv/bin/activate
     ```

   * **En Windows (usando PowerShell o CMD):**  
     ```
     .venv\Scripts\activate
     ```

   * Verás (.venv) al principio de la línea de tu terminal.

### **Paso 4: Instalar Dependencias**

Usa uv pip install para instalar todas las bibliotecas que necesita el proyecto.

1. **Dependencias de Producción:**  
   * (FastAPI, el servidor, el ORM y la configuración)  
     ``` bash
     uv pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
     ```

2. **Dependencias de Desarrollo:**  
   * (El framework de pruebas y el cliente HTTP para pruebas)  
     ``` bash
     uv pip install pytest httpx
     ```

### **Paso 5: Configurar la Base de Datos de Desarrollo**

La aplicación carga la URL de la base de datos desde un archivo .env.

1. **Crea el archivo .env:**  
   * Crea un nuevo archivo de texto llamado .env dentro de la carpeta backend/.  
   * La ruta completa debe ser: `sistema-inventarios/backend/.env` 
2. **Añade el contenido:**  
   * Abre el archivo y pega esta línea. Esto le dice a la app que use una base de datos SQLite llamada inventario.db (que se creará dentro de la carpeta backend).  
     ```
     DATABASE\_URL="sqlite:///./inventario.db"
     ```

### **Paso 6: Inicializar la Base de Datos**

Ahora tenemos que crear las tablas (productos, lotes, movimientos) en ese archivo inventario.db.

1. **Ejecuta el script de inicialización:**  
   * **Importante:** Asegúrate de estar en la carpeta **raíz** (sistema-inventarios), no en backend.  
     \# (Estando en la carpeta 'sistema-inventarios')  
     ```
      uv run python backend/app/db/init\_db.py
      ```

2. **Verifica:**  
   * Deberías ver el mensaje: Base de datos inicializada exitosamente.  
   * Ahora tendrás un nuevo archivo en backend/inventario.db.

### **Paso 7: Ejecutar el Servidor de Desarrollo**

¡Todo está listo\! Vamos a encender la API.

1. **Navega a la carpeta backend:**  
   * El servidor uvicorn debe ejecutarse desde la carpeta backend para que las importaciones de app funcionen.  
     ```
     cd backend
     ```

2. **Inicia el servidor:**  
   * Le decimos a uvicorn que ejecute el objeto app que se encuentra en el archivo app/main.py.  
   * `--reload` hace que el servidor se reinicie automáticamente cada vez que guardas un cambio en el código.  
     \# (Estando en la carpeta 'backend')  
     ```
     uv run uvicorn app.main:app \--reload
     ```

3. **¡Está vivo\!**  
   * Verás una salida como: Uvicorn running on http://127.0.0.1:8000  
   * Abre tu navegador y ve a [**http://127.0.0.1:8000/docs**](https://www.google.com/search?q=http://127.0.0.1:8000/docs) para ver la documentación interactiva de la API y probar los endpoints.

### **(Opcional) Ejecutar las Pruebas**

Para verificar que todo está configurado correctamente, puedes ejecutar nuestra suite de pruebas.

1. **Navega a la raíz del proyecto:**  
   * Si estás en la carpeta backend, vuelve a la raíz.  
     ```
     cd ..
     ```

2. **Ejecuta pytest:**  
   ```
   uv run pytest
   ```

* Deberías ver todos los tests pasar (ej: 23 passed).