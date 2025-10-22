# api/app.py
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "Reportes SIGA Updater", 
        "status": "running",
        "endpoints": {
            "update": "/api/update",
            "status": "/api/status"
        }
    })

@app.route('/api/update', methods=['POST'])
def update_data():
    return jsonify({"status": "success", "message": "Update endpoint - to be implemented"})

@app.route('/api/status')
def status():
    return jsonify({"status": "running", "timestamp": "2024-01-01T00:00:00Z"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)