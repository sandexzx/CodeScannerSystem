import time
import logging
import glob
import re
import json
import os
import pygame
from config_manager import load_config, SCANNER_FILE_PATH, SOUND_SUCCESS, SOUND_ERROR, SOUND_BOX_FULL, EXPORT_FILE, JSON_EXPORT_DIR, SESSION_BASE_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scanner.log'),
        logging.StreamHandler()
    ]
)

class ScannerHandler:
    def __init__(self, start_new_session=False):
        self.current_box = []
        self.box_number = 1
        self.processed_codes = set()
        pygame.mixer.init()
        
        # Load sound effects
        self.sound_success = pygame.mixer.Sound(SOUND_SUCCESS)
        self.sound_error = pygame.mixer.Sound(SOUND_ERROR)
        self.sound_box_full = pygame.mixer.Sound(SOUND_BOX_FULL)
        
        # Initialize JSON file handling
        self.json_base_name = os.path.join(JSON_EXPORT_DIR, EXPORT_FILE.split('/')[-1].replace('.xlsx', ''))
        
        # Initialize Excel file handling
        self.excel_dir = os.path.dirname(EXPORT_FILE)
        if start_new_session:
            self.create_new_session()
        else:
            self.load_existing_data()

    def get_latest_json_file(self):
        """Find the latest version of the JSON file"""
        pattern = f"{self.json_base_name}_*.json"
        files = glob.glob(pattern)
        
        if not files:
            # If no versioned files exist, check for the base file
            base_file = f"{self.json_base_name}.json"
            if os.path.exists(base_file):
                return base_file
            return None
            
        # Extract version numbers and find the latest
        versions = []
        for file in files:
            match = re.search(r'_(\d+)\.json$', file)
            if match:
                versions.append((int(match.group(1)), file))
        
        if not versions:
            return None
            
        # Return the file with the highest version number
        return max(versions, key=lambda x: x[0])[1]

    def get_next_version_number(self):
        """Get the next version number for a new session"""
        latest_file = self.get_latest_json_file()
        if not latest_file:
            return 1
            
        match = re.search(r'_(\d+)\.json$', latest_file)
        if match:
            return int(match.group(1)) + 1
        return 1

    def get_latest_session_number(self):
        """Find the latest session number from existing Excel files"""
        pattern = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_*.xlsx")
        files = glob.glob(pattern)
        
        if not files:
            return 0
            
        # Extract session numbers and find the latest
        versions = []
        for file in files:
            match = re.search(r'_(\d+)\.xlsx$', file)
            if match:
                versions.append(int(match.group(1)))
        
        return max(versions) if versions else 0

    def get_next_session_number(self):
        """Get the next session number"""
        return self.get_latest_session_number() + 1

    def create_new_session(self):
        """Create a new scanning session with new JSON and Excel files"""
        next_version = self.get_next_version_number()
        self.current_json_file = f"{self.json_base_name}_{next_version}.json"
        
        # Initialize new JSON file with empty array
        with open(self.current_json_file, 'w') as f:
            json.dump([], f, indent=4)
            
        # Create new Excel file for the session
        next_session = self.get_next_session_number()
        self.current_excel_file = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_{next_session}.xlsx")
        
        # Initialize Excel file with empty DataFrame
        import pandas as pd
        df = pd.DataFrame(columns=['Box Number', 'Code', 'Timestamp'])
        df.to_excel(self.current_excel_file, index=False)
            
        # Reset state
        self.current_box = []
        self.box_number = 1
        self.processed_codes = set()
        
        logging.info(f"Started new session with files: {self.current_json_file} and {self.current_excel_file}")

    def load_existing_data(self):
        """Load existing data from the latest JSON file and restore state"""
        import json
        
        self.current_json_file = self.get_latest_json_file()
        if not self.current_json_file:
            # If no existing file found, create a new session
            self.create_new_session()
            return
            
        # Set current Excel file based on the latest session
        latest_session = self.get_latest_session_number()
        self.current_excel_file = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_{latest_session}.xlsx")
            
        try:
            with open(self.current_json_file, 'r') as f:
                existing_data = json.load(f)
                
            if existing_data:
                # Get the last box number
                self.box_number = max(entry['Box Number'] for entry in existing_data)
                
                # Add all existing codes to processed_codes set
                self.processed_codes.update(entry['Code'] for entry in existing_data)
                
                # Get codes from the last box
                last_box_codes = [entry['Code'] for entry in existing_data 
                                if entry['Box Number'] == self.box_number]
                config = load_config()
                box_capacity = config['box_capacity']
                # If the last box wasn't full, restore it
                if len(last_box_codes) < box_capacity:
                    self.current_box = last_box_codes
                else:
                    # If the last box was full, start a new one
                    self.current_box = []
                    self.box_number += 1
                    
            logging.info(f"Restored state from {self.current_json_file}: Box {self.box_number}, {len(self.processed_codes)} processed codes")
        except Exception as e:
            logging.error(f"Error loading existing data: {str(e)}")
            # If there's an error, create a new session
            self.create_new_session()

    def play_sound(self, sound):
        """Safely play a sound with proper cleanup"""
        try:
            # Stop any currently playing sounds
            pygame.mixer.stop()
            # Play the new sound
            sound.play()
            # Wait a short moment to ensure sound starts playing
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Error playing sound: {str(e)}")

    def process_code(self, code):
        """Process a single scanned code"""
        code = code.strip()
        
        # Get current box capacity from config
        config = load_config()
        box_capacity = config['box_capacity']
        
        # Validate code (basic validation - can be extended)
        if not code or len(code) < 3:
            logging.warning(f"Invalid code format: {code}")
            return False
            
        # Check for duplicates
        if code in self.processed_codes:
            logging.warning(f"Duplicate code detected: {code}")
            self.play_sound(self.sound_error)
            return False
            
        # Add code to current box
        self.current_box.append(code)
        self.processed_codes.add(code)
        self.play_sound(self.sound_success)
        
        element_number = len(self.current_box)
        logging.info(f"Code added to box {self.box_number} (element {element_number}/{box_capacity}): {code}")
        
        # Save to JSON and Excel after each scan
        self.save_json_data(code)
        self.save_box_data()
        
        # Check if box is full
        if len(self.current_box) >= box_capacity:
            self.play_sound(self.sound_box_full)
            logging.info(f"Box {self.box_number} is full!")
            self.create_new_box()
            
        return True

    def save_json_data(self, code):
        """Save single code data to JSON file"""
        import json
        from datetime import datetime
        
        try:
            with open(self.current_json_file, 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
            
        # Create new entry
        new_entry = {
            'Box Number': self.box_number,
            'Code': code,
            'Timestamp': datetime.now().isoformat()
        }
        
        existing_data.append(new_entry)
        
        with open(self.current_json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)
        logging.info(f"Code {code} saved to {self.current_json_file}")

    def save_box_data(self):
        """Save box data to Excel file"""
        import pandas as pd
        from datetime import datetime
        
        data = {
            'Box Number': [self.box_number] * len(self.current_box),
            'Code': self.current_box,
            'Timestamp': [datetime.now()] * len(self.current_box)
        }
        
        df = pd.DataFrame(data)
        
        # Save to Excel
        try:
            existing_df = pd.read_excel(self.current_excel_file)
            if not existing_df.empty:
                # Remove entries for current box if they exist
                existing_df = existing_df[existing_df['Box Number'] != self.box_number]
                # Only concatenate if we have data to add
                if not df.empty:
                    df = pd.concat([existing_df, df], ignore_index=True)
                else:
                    df = existing_df
        except FileNotFoundError:
            pass
            
        df.to_excel(self.current_excel_file, index=False)
        logging.info(f"Box {self.box_number} data saved to {self.current_excel_file}")

    def create_new_box(self):
        """Create a new box and save the current one"""
        if self.current_box:
            # Create new box
            self.current_box = []
            self.box_number += 1
            logging.info(f"Created new box {self.box_number}")

    def start_monitoring(self):
        """Start monitoring for scanner input"""
        print("\n=== Сканер запущен! ===")
        print("Вводите коды (для выхода введите 'exit' или нажмите Ctrl+C)")
        print("Для принудительного закрытия коробки введите 'box'")
        print("================================================")
        
        try:
            while True:
                code = input("\nВведите код: ").strip()
                
                if code.lower() == 'exit':
                    print("\nЗавершение работы сканера...")
                    break
                    
                if code.lower() == 'box':
                    if self.current_box:
                        print(f"\nПринудительное закрытие коробки {self.box_number}...")
                        self.play_sound(self.sound_box_full)
                        self.create_new_box()
                        print(f"Создана новая коробка {self.box_number}")
                    else:
                        print("\nТекущая коробка пуста!")
                    continue
                    
                if code:
                    self.process_code(code)
                else:
                    print("Код не может быть пустым!")
                    
        except KeyboardInterrupt:
            print("\n\nЗавершение работы сканера...")
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
        finally:
            print("\nСканер остановлен.")

def main():
    while True:
        print("\n=== Меню ===")
        print("1. Начать новую сессию сканирования")
        print("2. Продолжить существующую сессию")
        print("3. Выход")
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == '1':
            handler = ScannerHandler(start_new_session=True)
            handler.start_monitoring()
        elif choice == '2':
            handler = ScannerHandler(start_new_session=False)
            handler.start_monitoring()
        elif choice == '3':
            print("\nЗавершение работы программы...")
            break
        else:
            print("\nНеверный выбор. Пожалуйста, выберите 1-3.")

if __name__ == "__main__":
    main() 