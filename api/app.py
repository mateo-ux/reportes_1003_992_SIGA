# api/app.py
from flask import Flask, jsonify, request
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.api_client import SIGAClient
from utils.database import DatabaseManager
from datetime import datetime
import threading

app = Flask(__name__)

# Variable global para el estado
update_status = {
    "running": False,
    "last_run": None,
    "success": False,
    "message": ""
}

def background_update():
    """Ejecutar actualización en segundo plano"""
    global update_status
    
    update_status["running"] = True
    update_status["success"] = False
    update_status["message"] = "Iniciando actualización..."
    
    try:
        client = SIGAClient()
        db = DatabaseManager()
        
        conn = db.connect()
        if not conn:
            update_status["message"] = "Error conectando a la base de datos"
            return
        
        # Autenticar
        if not client.authenticate():
            update_status["message"] = "Error de autenticación en SIGA"
            return
        
        # Obtener datos
        aspirantes_data = client.get_reporte_1003()
        estudiantes_data = client.get_reporte_992_completo()
        
        if not aspirantes_data and not estudiantes_data:
            update_status["message"] = "No se pudieron descargar datos"
            return
        
        # Procesar datos
        if aspirantes_data:
            db.create_aspirantes_table(conn)
            db.insert_aspirantes_data(conn, aspirantes_data)
        
        if estudiantes_data:
            db.create_estudiantes_table(conn)
            db.insert_estudiantes_data(conn, estudiantes_data)
        
        # Éxito
        stats = db.get_database_stats(conn)
        update_status["success"] = True
        update_status["message"] = f"Actualización exitosa. Aspirantes: {stats.get('aspirantes', 0):,}, Estudiantes: {stats.get('estudiantes', 0):,}"
        
        conn.close()
        
    except Exception as e:
        update_status["message"] = f"Error: {str(e)}"
    finally:
        update_status["running"] = False
        update_status["last_run"] = datetime.now().isoformat()

@app.route('/')
def home():
    """Página de inicio"""
    return jsonify({
        "service": "TalentoTech Data Updater",
        "status": "running",
        "endpoints": {
            "update": "/api/update",
            "status": "/api/status"
        }
    })

@app.route('/api/update', methods=['POST'])
def trigger_update():
    """Ejecutar actualización de datos"""
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
        "message": "Actualización iniciada en segundo plano",
        "check_status": "/api/status"
    })

@app.route('/api/status')
def get_status():
    """Obtener estado de la actualización"""
    db = DatabaseManager()
    conn = db.connect()
    stats = db.get_database_stats(conn) if conn else {}
    conn.close() if conn else None
    
    return jsonify({
        "update_status": update_status,
        "database_stats": stats,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)