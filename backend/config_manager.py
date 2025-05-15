import json
import os

DEFAULT_CONFIG = {
    "scanner_file_path": "scanner_data.txt",
    "box_capacity": 12,
    "sound_success": "sounds/success.wav",
    "sound_error": "sounds/error.wav",
    "sound_box_full": "sounds/box_full.wav",
    "export_file": "export/EXCEL/boxes.xlsx",
    "json_export_dir": "export/JSON",
    "session_base_name": "session"
}

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from JSON file or create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
                # Merge with default config to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(existing_config)
                # Save updated config back to file
                save_config(config)
                return config
        except json.JSONDecodeError:
            print("Ошибка чтения конфигурации. Используются настройки по умолчанию.")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to JSON file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def update_box_capacity(new_capacity):
    """Update box capacity in config and return updated config"""
    config = load_config()
    config['box_capacity'] = new_capacity
    save_config(config)
    return config

# Load initial configuration
config = load_config()

# Export settings as module variables
SCANNER_FILE_PATH = config["scanner_file_path"]
BOX_CAPACITY = config["box_capacity"]
SOUND_SUCCESS = config["sound_success"]
SOUND_ERROR = config["sound_error"]
SOUND_BOX_FULL = config["sound_box_full"]
EXPORT_FILE = config["export_file"]
JSON_EXPORT_DIR = config["json_export_dir"]
SESSION_BASE_NAME = config["session_base_name"]

# Create necessary directories
os.makedirs("sounds", exist_ok=True)
os.makedirs("export/EXCEL", exist_ok=True)
os.makedirs("export/JSON", exist_ok=True) 