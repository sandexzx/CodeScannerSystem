from flask import Flask, request, jsonify
from flask_cors import CORS
from scanner_handler import ScannerHandler
from config_manager import load_config, update_box_capacity
import json
import os
from datetime import datetime
import argparse

app = Flask(__name__)

# Простая настройка CORS для всех маршрутов
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        config = load_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/box-capacity', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        if not data or 'capacity' not in data:
            return jsonify({'error': 'Capacity is required'}), 400
            
        capacity = int(data['capacity'])
        if capacity <= 0:
            return jsonify({'error': 'Capacity must be positive'}), 400
            
        config = update_box_capacity(capacity)
        return jsonify({'box_capacity': config['box_capacity']})
    except ValueError:
        return jsonify({'error': 'Invalid capacity value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def scan_code():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Code is required'}), 400
            
        handler = ScannerHandler(start_new_session=False)
        result = handler.process_code(data['code'])
        if result is not False:
            return jsonify({"result": result})
        return jsonify({'error': 'Invalid code'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-session', methods=['POST'])
def start_session():
    try:
        handler = ScannerHandler(start_new_session=True)
        return jsonify({
            "sessionId": handler.current_json_file,
            "startTime": datetime.now().isoformat(),
            "boxCapacity": load_config()['box_capacity'],
            "scannedItems": 0,
            "currentBoxItems": 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/continue-session', methods=['POST'])
def continue_session():
    try:
        handler = ScannerHandler(start_new_session=False)
        if not handler.current_json_file:
            return jsonify({'error': 'No existing session found'}), 404
        
        with open(handler.current_json_file, 'r') as f:
            data = json.load(f)
            
        # Calculate current session stats
        scanned_items = len(data)
        current_box_items = len([item for item in data if item['Box Number'] == handler.box_number])
        
        return jsonify({
            "sessionId": handler.current_json_file,
            "startTime": datetime.fromtimestamp(os.path.getctime(handler.current_json_file)).isoformat(),
            "boxCapacity": load_config()['box_capacity'],
            "scannedItems": scanned_items,
            "currentBoxItems": current_box_items
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete-session', methods=['POST'])
def complete_session():
    # This endpoint is currently a placeholder as the session completion
    # is handled by the frontend state management
    return jsonify({"status": "success"})

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        handler = ScannerHandler(start_new_session=False)
        json_path = handler.get_latest_json_file()
        if not json_path or not os.path.exists(json_path):
            return jsonify([])
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/clear-export', methods=['POST'])
def clear_export_folder():
    try:
        # Get the export directories from config
        config = load_config()
        excel_dir = os.path.dirname(config['export_file'])
        json_dir = config['json_export_dir']
        
        # Clear Excel directory
        for file in os.listdir(excel_dir):
            file_path = os.path.join(excel_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        # Clear JSON directory
        for file in os.listdir(json_dir):
            file_path = os.path.join(json_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
        return jsonify({"status": "success", "message": "Export folders cleared successfully"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask API server')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    args = parser.parse_args()
    
    app.run(port=args.port, host=args.host) 