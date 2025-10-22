# main.py
from flask import Flask, jsonify, request
import os
from scripts.actualizar_datos import ActualizadorMultiReportes
from scripts.exportar_excel import ExportadorExcel
import threading
import uuid
from datetime import datetime

app = Flask(__name__)

# Almacenamiento simple para jobs (en producción usar Redis)
jobs = {}

@app.route('/')
def home():
    return jsonify({
        "message": "TalentoTech Data API",
        "endpoints": {
            "actualizar_datos": "/api/actualizar",
            "exportar_excel": "/api/exportar",
            "estado_job": "/api/job/<job_id>"
        }
    })

@app.route('/api/actualizar', methods=['POST'])
def actualizar_datos():
    """Endpoint para actualizar datos desde la API"""
    job_id = str(uuid.uuid4())
    
    def ejecutar_actualizacion():
        try:
            actualizador = ActualizadorMultiReportes()
            success = actualizador.ejecutar_actualizacion_completa()
            jobs[job_id] = {
                "status": "completed" if success else "failed",
                "message": "Actualización completada" if success else "Error en actualización",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            jobs[job_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    jobs[job_id] = {"status": "running", "message": "Iniciando actualización..."}
    thread = threading.Thread(target=ejecutar_actualizacion)
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "message": "Actualización iniciada en segundo plano",
        "status_url": f"/api/job/{job_id}"
    })

@app.route('/api/exportar', methods=['POST'])
def exportar_excel():
    """Endpoint para exportar datos a Excel"""
    job_id = str(uuid.uuid4())
    
    def ejecutar_exportacion():
        try:
            exportador = ExportadorExcel()
            success = exportador.ejecutar_exportacion_completa()
            jobs[job_id] = {
                "status": "completed" if success else "failed",
                "message": "Exportación completada" if success else "Error en exportación",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            jobs[job_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    jobs[job_id] = {"status": "running", "message": "Iniciando exportación..."}
    thread = threading.Thread(target=ejecutar_exportacion)
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "message": "Exportación iniciada en segundo plano",
        "status_url": f"/api/job/{job_id}"
    })

@app.route('/api/job/<job_id>')
def get_job_status(job_id):
    """Obtener estado de un job"""
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job no encontrado"}), 404
    
    return jsonify({
        "job_id": job_id,
        "status": job["status"],
        "message": job["message"],
        "timestamp": job["timestamp"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)