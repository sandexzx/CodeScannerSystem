from flask import Flask, request, jsonify
from flask_cors import CORS
from scanner_handler import ScannerHandler
from config_manager import load_config, update_box_capacity
import json
import os
from datetime import datetime
import argparse
import logging

def read_jsonl_file(filepath):
    """Helper function to read JSONL file and return data as list"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Пропускаем пустые строки
                    try:
                        entry = json.loads(line)
                        data.append(entry)
                    except json.JSONDecodeError as je:
                        logging.warning(f"Ignoring invalid JSON on line {line_num} in {filepath}: {str(je)}")
                        continue
    except Exception as e:
        logging.error(f"Error reading JSONL file {filepath}: {str(e)}")
        raise
    return data

def read_json_or_jsonl_file(filepath):
    """Helper function to read both JSON and JSONL files"""
    if filepath.endswith('.jsonl'):
        return read_jsonl_file(filepath)
    else:
        # Legacy JSON file support
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

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
        
        # Быстрое чтение последних данных из JSON/JSONL файла
        data = read_json_or_jsonl_file(handler.current_json_file)
            
        # Быстрый подсчет статистики
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
            
        data = read_json_or_jsonl_file(json_path)
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

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    try:
        handler = ScannerHandler(start_new_session=False)
        success = handler.generate_excel_from_json()
        
        if success:
            return jsonify({
                "status": "success", 
                "message": "Excel файл успешно создан",
                "excel_file": handler.current_excel_file
            })
        else:
            return jsonify({"status": "error", "message": "Не удалось создать Excel файл"}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/excel-status', methods=['GET'])
def excel_status():
    try:
        handler = ScannerHandler(start_new_session=False)
        excel_exists = os.path.exists(handler.current_excel_file)
        json_exists = os.path.exists(handler.current_json_file)
        
        return jsonify({
            "excel_exists": excel_exists,
            "json_exists": json_exists,
            "excel_file": handler.current_excel_file if excel_exists else None,
            "json_file": handler.current_json_file if json_exists else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask API server')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    args = parser.parse_args()
    
    app.run(port=args.port, host=args.host) 