# api/app.py
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
    "message": "Servicio iniciado"
}

def background_update():
    """Simulación de actualización en segundo plano"""
    global update_status
    update_status["running"] = True
    update_status["message"] = "Actualización en progreso..."
    
    try:
        # Simular trabajo pesado
        time.sleep(10)
        
        # Aquí iría tu lógica real de actualización
        # from utils.api_client import SIGAClient
        # from utils.database import DatabaseManager
        # ... tu código de actualización
        
        update_status["success"] = True
        update_status["message"] = "✅ Actualización completada exitosamente"
        
    except Exception as e:
        update_status["success"] = False
        update_status["message"] = f"❌ Error: {str(e)}"
    finally:
        update_status["running"] = False
        update_status["last_run"] = datetime.now().isoformat()

@app.route('/')
def home():
    return jsonify({
        "service": "Reportes SIGA API",
        "status": "running",
        "endpoints": {
            "update": "POST /api/update",
            "status": "GET /api/status"
        }
    })

@app.route('/api/update', methods=['POST'])
def trigger_update():
    global update_status
    
    if update_status["running"]:
        return jsonify({
            "status": "error",
            "message": "Ya hay una actualización en curso"
        }), 409
    
    # Iniciar en segundo plano
    thread = threading.Thread(target=background_update)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "success",
        "message": "Actualización iniciada en segundo plano",
        "check_status": "/api/status"
    })

@app.route('/api/status')
def get_status():
    return jsonify({
        "update_status": update_status,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)