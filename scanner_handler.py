import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygame
from config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scanner.log'),
        logging.StreamHandler()
    ]
)

class ScannerFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.current_box = []
        self.box_number = 1
        self.processed_codes = set()
        pygame.mixer.init()
        
        # Load sound effects
        self.sound_success = pygame.mixer.Sound(SOUND_SUCCESS)
        self.sound_error = pygame.mixer.Sound(SOUND_ERROR)
        self.sound_box_full = pygame.mixer.Sound(SOUND_BOX_FULL)
        
        # Create scanner file if it doesn't exist
        if not os.path.exists(SCANNER_FILE_PATH):
            with open(SCANNER_FILE_PATH, 'w') as f:
                pass

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
        logging.info(f"Code added to box {self.box_number} (element {element_number}/{BOX_CAPACITY}): {code}")
        
        # Save to JSON after each scan
        self.save_json_data(code)
        
        # Check if box is full
        if len(self.current_box) >= BOX_CAPACITY:
            self.play_sound(self.sound_box_full)
            logging.info(f"Box {self.box_number} is full!")
            self.create_new_box()
            
        return True

    def save_json_data(self, code):
        """Save single code data to JSON file"""
        import json
        from datetime import datetime
        
        json_file = EXPORT_FILE.replace('.xlsx', '.json')
        try:
            with open(json_file, 'r') as f:
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
        
        with open(json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)
        logging.info(f"Code {code} saved to {json_file}")

    def create_new_box(self):
        """Create a new box and save the current one"""
        if self.current_box:
            # Save current box data
            self.save_box_data()
            # Create new box
            self.current_box = []
            self.box_number += 1
            logging.info(f"Created new box {self.box_number}")

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
            existing_df = pd.read_excel(EXPORT_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            pass
            
        df.to_excel(EXPORT_FILE, index=False)
        logging.info(f"Box {self.box_number} data saved to {EXPORT_FILE}")

    def on_modified(self, event):
        if event.src_path == os.path.abspath(SCANNER_FILE_PATH):
            try:
                # Читаем содержимое файла
                with open(SCANNER_FILE_PATH, 'r') as f:
                    content = f.read().strip()
                    
                # Если файл пустой, пропускаем обработку
                if not content:
                    return
                    
                # Обрабатываем содержимое
                if FILE_FORMAT == "csv":
                    codes = content.split(',')
                    for code in codes:
                        if code.strip():  # Проверяем, что код не пустой
                            self.process_code(code)
                else:  # single_line
                    codes = content.split('\n')
                    for code in codes:
                        if code.strip():  # Проверяем, что код не пустой
                            self.process_code(code)
                            
                # Очищаем файл только после успешной обработки
                with open(SCANNER_FILE_PATH, 'w') as f:
                    pass
                    
            except Exception as e:
                logging.error(f"Error processing file: {str(e)}")
                # В случае ошибки не очищаем файл, чтобы не потерять данные

def start_monitoring():
    """Start monitoring the scanner file"""
    event_handler = ScannerFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(SCANNER_FILE_PATH)), recursive=False)
    observer.start()
    
    logging.info(f"Started monitoring {SCANNER_FILE_PATH}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Monitoring stopped")
        
    observer.join()

if __name__ == "__main__":
    start_monitoring() 