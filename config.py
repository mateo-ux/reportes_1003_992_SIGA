# config_api.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la API
API_CONFIG = {
    'base_url_produccion': 'https://siga.talentotech2.com.co/siga_new/web/app.php/api/rest',
    'client_id': 'talentotech2_webservice',
    'secreto': 'LcU54XCSqzRU',
    'database_url': os.getenv('DATABASE_URL'),
    
    # Timeouts
    'timeout_token': 30,
    'timeout_report': 60,
    'timeout_auth': 30,
    
    # Tamaños de lote
    'lote_size_db': 500,
    'lote_size_api': 1000
}