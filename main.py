from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import psycopg
import os
import time
import socket
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

app = FastAPI(title="API Reportes SIGA", version="1.0.0")

class ActualizadorMultiReportes:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        
        # Diferentes endpoints para probar
        self.base_urls = [
            "https://siga.talentotech2.com.co/siga_new/web/app.php/api/rest",
            "http://talentotech2prueba.datasae.com/siga_new/web/app.php/api/rest"
        ]
        self.current_base_url = None
        
        self.client_id = "talentotech2_webservice"
        self.secreto = "LcU54XCSqzRU"
        self.access_token = None
        self.auth_token = None
        
        # Credenciales desde .env
        self.siga_username = os.getenv('SIGA_USERNAME', 'api_user')
        self.siga_password = os.getenv('SIGA_PASSWORD', 'Api_user123*')
        
        # Lista de periodos académicos según los proporcionados
        self.periodos_academicos = [
            '2024090208', '2024091608', '2024100708', 
            '2024101510', '2025011112', '2025012710'
        ]

    # ... (mantener todos los métodos de la clase igual que en tu código original)

    def ejecutar_actualizacion_completa(self):
        """Ejecutar proceso completo para ambos reportes"""
        # ... (mantener el método igual)

# Endpoints de la API
class UpdateRequest(BaseModel):
    secret_key: str

@app.get("/")
def read_root():
    return {"message": "API Reportes SIGA - Funcionando", "status": "active"}

@app.post("/actualizar-reportes")
async def actualizar_reportes(request: UpdateRequest):
    """Endpoint para ejecutar la actualización desde Apps Script"""
    
    # Verificar clave secreta
    expected_key = os.getenv('API_SECRET_KEY')
    if not expected_key or request.secret_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        actualizador = ActualizadorMultiReportes()
        success = actualizador.ejecutar_actualizacion_completa()
        
        return {
            "status": "success" if success else "error",
            "message": "Actualización completada" if success else "Error en la actualización",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/estado")
def obtener_estado():
    """Endpoint para verificar el estado del servicio"""
    try:
        actualizador = ActualizadorMultiReportes()
        conn = actualizador.conectar_bd()
        
        if conn:
            with conn.cursor() as cur:
                # Verificar tablas y conteos
                estado = {"database": "connected"}
                
                try:
                    cur.execute("SELECT COUNT(*) FROM aspirantes;")
                    estado["aspirantes"] = cur.fetchone()[0]
                except:
                    estado["aspirantes"] = 0
                    
                try:
                    cur.execute("SELECT COUNT(*) FROM estudiantes;")
                    estado["estudiantes"] = cur.fetchone()[0]
                except:
                    estado["estudiantes"] = 0
                    
                conn.close()
        else:
            estado = {"database": "disconnected"}
            
        return estado
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)