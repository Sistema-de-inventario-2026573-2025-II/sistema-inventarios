import logging
import requests
import pandas as pd

logger = logging.getLogger(__name__)

def fetch_top_available_products(api_url: str, top_n: int = 5) -> pd.DataFrame:
    """
    Función que llama al endpoint de reporte de productos con mayor disponibilidad
    y devuelve los datos en un DataFrame de pandas.
    """
    endpoint = f"{api_url}/reportes/top-productos-disponibles"
    params = {"top_n": top_n}
    
    logger.info(f"Llamando al endpoint {endpoint} con top_n={top_n}...")
    response = requests.get(endpoint, params=params)
    
    if response.status_code != 200:
        logger.error(f"Error al llamar al endpoint: {response.status_code} - {response.text}")
        response.raise_for_status()
    
    data = response.json()
    logger.info(f"Datos recibidos: {data}")
    
    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(data)
    logger.info(f"DataFrame creado con {df.shape[0]} filas y {df.shape[1]} columnas.")
    
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example usage:
    # Replace with your actual API URL
    API_BASE_URL = "http://localhost:8000/api/v1" 
    
    print("Fetching top 3 available products:")
    top_products_df = fetch_top_available_products(API_BASE_URL, top_n=3)
    print(top_products_df)

    print("\nFetching top 5 available products:")
    top_products_df_5 = fetch_top_available_products(API_BASE_URL, top_n=5)
    print(top_products_df_5)