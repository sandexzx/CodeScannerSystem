import time
import logging
import glob
import re
import json
import os
import pygame
from config_manager import load_config, SCANNER_FILE_PATH, SOUND_SUCCESS, SOUND_ERROR, SOUND_BOX_FULL, EXPORT_FILE, JSON_EXPORT_DIR, SESSION_BASE_NAME
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from rich import print as rprint
from datetime import datetime
from rich.prompt import Prompt

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

console = Console()

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
        self.json_base_name = os.path.join(JSON_EXPORT_DIR, SESSION_BASE_NAME)
        
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
            mod_time = os.path.getmtime(file)
            versions.append((mod_time, file))
        
        if not versions:
            return None
            
        # Return the file with the highest version number
        return max(versions, key=lambda x: x[0])[1]

    def get_latest_session_number(self):
        """Find the latest session number from existing Excel files"""
        pattern = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_*.xlsx")
        files = glob.glob(pattern)
        
        # Просто проверяем наличие файлов
        return 1 if files else 0

    def create_new_session(self):
        """Create a new scanning session with new JSON and Excel files"""
        # Create necessary directories if they don't exist
        os.makedirs(os.path.dirname(self.json_base_name), exist_ok=True)
        os.makedirs(self.excel_dir, exist_ok=True)
        
        # Получаем текущую дату и время в нужном формате
        timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
        self.current_json_file = f"{self.json_base_name}_{timestamp}.json"
        
        # Initialize new JSON file with empty array
        with open(self.current_json_file, 'w') as f:
            json.dump([], f, indent=4)
            
        # Create new Excel file for the session
        # Используем тот же timestamp для Excel файла
        self.current_excel_file = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_{timestamp}.xlsx")
        
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
            
        # Извлекаем дату и время из имени JSON файла
        json_filename = os.path.basename(self.current_json_file)
        match = re.search(r'_(\d{2}_\d{2}_\d{2}_\d{2}_\d{2})\.json$', json_filename)
        if match:
            timestamp = match.group(1)
            # Формируем имя Excel файла с тем же таймстампом
            self.current_excel_file = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_{timestamp}.xlsx")
        else:
            # Если не удалось извлечь таймстамп, ищем последний Excel файл
            pattern = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_*.xlsx")
            files = glob.glob(pattern)
            if files:
                self.current_excel_file = max(files, key=os.path.getmtime)
            else:
                # Если вообще ничего нет, создаем новую сессию
                self.create_new_session()
                return
            
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
            # Убираем задержку, так как она не нужна
        except Exception as e:
            logging.error(f"Error playing sound: {str(e)}")

    def process_code(self, code):
        """Process a single scanned code"""
        code = code.strip()
        
        # Get current box capacity from config
        config = load_config()
        box_capacity = config['box_capacity']
        
        # Validate code (basic validation - can be extended)
        if not code:
            console.print(f"[red]Неверный формат кода: пустой код[/red]")
            self.play_sound(self.sound_error)
            return False
            
        if len(code) < 3:
            console.print(f"[red]Неверный формат кода: код слишком короткий ({code})[/red]")
            self.play_sound(self.sound_error)
            return False
            
        # Check for duplicates
        if code in self.processed_codes:
            console.print(f"[yellow]Обнаружен дубликат кода: {code}[/yellow]")
            self.play_sound(self.sound_error)
            return False
            
        # Add code to current box
        self.current_box.append(code)
        self.processed_codes.add(code)
        
        # Воспроизводим звук успеха асинхронно
        import threading
        threading.Thread(target=self.play_sound, args=(self.sound_success,)).start()
        
        element_number = len(self.current_box)
        console.print(f"[green]Код добавлен в коробку {self.box_number} (элемент {element_number}/{box_capacity}): {code}[/green]")
        
        # Сохраняем данные асинхронно
        threading.Thread(target=self.save_json_data, args=(code,)).start()
        threading.Thread(target=self.save_box_data).start()
        
        # Check if box is full
        if len(self.current_box) >= box_capacity:
            # Воспроизводим звук заполнения коробки асинхронно
            threading.Thread(target=self.play_sound, args=(self.sound_box_full,)).start()
            console.print(Panel.fit(
                f"[bold red]Коробка {self.box_number} заполнена![/bold red]",
                border_style="red"
            ))
            self.create_new_box()
            
        return code  # Return the validated code instead of True

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
        console.print(f"[blue]Код {code} сохранен в {self.current_json_file}[/blue]")

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
        console.print(f"[blue]Данные коробки {self.box_number} сохранены в {self.current_excel_file}[/blue]")

    def create_new_box(self):
        """Create a new box and save current box data"""
        self.current_box = []
        self.box_number += 1
        console.print(Panel.fit(
            f"[bold green]Создана новая коробка #{self.box_number}[/bold green]",
            border_style="green"
        ))

    def start_monitoring(self):
        """Start monitoring for scanner input"""
        console.print(Panel.fit(
            "[bold blue]Сканер запущен![/bold blue]\n"
            "[yellow]Вводите коды (для выхода нажмите Ctrl+C)[/yellow]",
            border_style="blue"
        ))
        
        try:
            while True:
                code = Prompt.ask("\nВведите код").strip()
                
                if code:
                    self.process_code(code)
                else:
                    console.print("[red]Код не может быть пустым![/red]")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Мониторинг остановлен пользователем[/yellow]")
        except Exception as e:
            console.print(f"[red]Ошибка при мониторинге: {str(e)}[/red]")

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