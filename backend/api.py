from flask import Flask, jsonify, request
from flask_cors import CORS
from config_manager import load_config, update_box_capacity

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        config = load_config()
        return jsonify({
            'box_capacity': config['box_capacity']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/box-capacity', methods=['POST'])
def update_box_capacity_endpoint():
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

if __name__ == '__main__':
    app.run(port=5001, host='127.0.0.1') 