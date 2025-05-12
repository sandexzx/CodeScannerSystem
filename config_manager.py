import json
import os

DEFAULT_CONFIG = {
    "scanner_file_path": "scanner_data.txt",
    "file_format": "single_line",
    "box_capacity": 12,
    "sound_success": "sounds/success.wav",
    "sound_error": "sounds/error.wav",
    "sound_box_full": "sounds/box_full.wav",
    "export_file": "export/boxes.xlsx"
}

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from JSON file or create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
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

# Load initial configuration
config = load_config()

# Export settings as module variables
SCANNER_FILE_PATH = config["scanner_file_path"]
FILE_FORMAT = config["file_format"]
BOX_CAPACITY = config["box_capacity"]
SOUND_SUCCESS = config["sound_success"]
SOUND_ERROR = config["sound_error"]
SOUND_BOX_FULL = config["sound_box_full"]
EXPORT_FILE = config["export_file"]

# Create necessary directories
os.makedirs("sounds", exist_ok=True)
os.makedirs("export", exist_ok=True) 