from flask import Flask, jsonify, request
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Estado global de la actualización
update_status = {
    "running": False,
    "last_run": None,
    "success": False,
    "message": "Servicio iniciado - Listo para actualizar"
}

def background_update():
    """Ejecutar actualización en segundo plano"""
    global update_status
    update_status["running"] = True
    update_status["message"] = "🔄 Actualización en progreso..."
    
    try:
        # Simular trabajo de actualización
        time.sleep(5)
        
        # Aquí irá tu lógica real de actualización
        # from utils.api_client import SIGAClient
        # from utils.database import DatabaseManager
        
        update_status["success"] = True
        update_status["message"] = "✅ Actualización completada exitosamente"
        
    except Exception as e:
        update_status["success"] = False
        update_status["message"] = f"❌ Error en actualización: {str(e)}"
    finally:
        update_status["running"] = False
        update_status["last_run"] = datetime.now().isoformat()

@app.route('/')
def home():
    return jsonify({
        "service": "Reportes SIGA API",
        "status": "active",
        "version": "1.0",
        "endpoints": {
            "actualizar_datos": "POST /api/update",
            "estado": "GET /api/status",
            "salud": "GET /health"
        }
    })

@app.route('/api/update', methods=['POST'])
def trigger_update():
    """Ejecutar actualización de datos desde Apps Script"""
    global update_status
    
    if update_status["running"]:
        return jsonify({
            "status": "error",
            "message": "Ya hay una actualización en curso"
        }), 409
    
    # Iniciar actualización en segundo plano
    thread = threading.Thread(target=background_update)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "success",
        "message": "✅ Actualización iniciada en segundo plano",
        "check_status": "/api/status"
    })

@app.route('/api/status')
def get_status():
    """Obtener estado de la actualización"""
    return jsonify({
        "update_status": update_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Endpoint de salud para monitoreo"""
    return jsonify({
        "status": "healthy",
        "service": "reportes-siga-api",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)