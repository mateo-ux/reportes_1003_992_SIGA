# api/app.py
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "Reportes SIGA Updater",
        "status": "active", 
        "endpoints": {
            "update": "POST /api/update",
            "status": "GET /api/status"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/update', methods=['POST'])
def update_data():
    try:
        # Aquí irá tu lógica de actualización
        return jsonify({
            "status": "success",
            "message": "Actualización iniciada"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/status')
def status():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)