import json
import os
import time
import logging

DEFAULT_CONFIG = {
    "scanner_file_path": "scanner_data.txt",
    "box_capacity": 12,
    "sound_success": "sounds/success.wav",
    "sound_error": "sounds/error.wav",
    "sound_box_full": "sounds/box_full.wav",
    "export_file": "export/EXCEL/boxes.xlsx",
    "json_export_dir": "export/JSON",
    "session_base_name": "session",
    # SMTP / email settings for sending exported Excel
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_password": "",
    "smtp_use_tls": True,
    "mail_from": "",
    "mail_to": ""
}

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from JSON file or create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        max_retries = 5
        base_delay = 0.1  # 100ms base delay
        
        for attempt in range(max_retries):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    config = DEFAULT_CONFIG.copy()
                    config.update(existing_config)
                    # Save updated config back to file
                    save_config(config)
                    return config
            except (json.JSONDecodeError, IOError, OSError) as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f"Попытка {attempt + 1} чтения конфигурации не удалась: {str(e)}. Повтор через {delay:.2f}с")
                    print(f"Ошибка чтения конфигурации (попытка {attempt + 1}/{max_retries}). Повтор через {delay:.2f}с...")
                    time.sleep(delay)
                else:
                    logging.error(f"Не удалось прочитать конфигурацию после {max_retries} попыток: {str(e)}. Используются настройки по умолчанию.")
                    print(f"Критическая ошибка: не удалось прочитать конфигурацию после {max_retries} попыток. Используются настройки по умолчанию.")
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
