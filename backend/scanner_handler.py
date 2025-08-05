import time
import logging
import glob
import re
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
import pandas as pd
import threading
from pathlib import Path
import msvcrt  # For Windows file locking

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
        """Find the latest version of the JSONL file"""
        pattern = f"{self.json_base_name}_*.jsonl"
        files = glob.glob(pattern)
        
        if not files:
            # If no versioned files exist, check for the base file
            base_file = f"{self.json_base_name}.jsonl"
            if os.path.exists(base_file):
                return base_file
            # Also check for old .json files for backward compatibility
            old_json_pattern = f"{self.json_base_name}_*.json"
            old_files = glob.glob(old_json_pattern)
            if old_files:
                # Return the latest old JSON file
                versions = [(os.path.getmtime(file), file) for file in old_files]
                return max(versions, key=lambda x: x[0])[1]
            return None
            
        # Extract modification times and find the latest
        versions = []
        for file in files:
            mod_time = os.path.getmtime(file)
            versions.append((mod_time, file))
        
        if not versions:
            return None
            
        # Return the file with the latest modification time
        return max(versions, key=lambda x: x[0])[1]

    def get_latest_session_number(self):
        """Find the latest session number from existing Excel files"""
        pattern = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_*.xlsx")
        files = glob.glob(pattern)
        
        # Просто проверяем наличие файлов
        return 1 if files else 0

    def create_new_session(self):
        """Create a new scanning session with new JSONL and Excel files"""
        # Create necessary directories if they don't exist
        os.makedirs(os.path.dirname(self.json_base_name), exist_ok=True)
        os.makedirs(self.excel_dir, exist_ok=True)
        
        # Получаем текущую дату и время в нужном формате
        timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
        self.current_json_file = f"{self.json_base_name}_{timestamp}.jsonl"
        
        # Initialize new JSONL file (empty file - will be appended to)
        with open(self.current_json_file, 'w', encoding='utf-8'):
            pass  # Create empty file
            
        # Create new Excel file for the session
        # Используем тот же timestamp для Excel файла
        self.current_excel_file = os.path.join(self.excel_dir, f"{SESSION_BASE_NAME}_{timestamp}.xlsx")
        
        # Initialize Excel file with empty DataFrame
        df = pd.DataFrame(columns=['Box Number', 'Code', 'Timestamp'])
        df.to_excel(self.current_excel_file, index=False)
            
        # Reset state
        self.current_box = []
        self.box_number = 1
        self.processed_codes = set()
        
        logging.info(f"Started new session with files: {self.current_json_file} and {self.current_excel_file}")

    def load_existing_data(self):
        """Load existing data from the latest JSONL file and restore state"""
        import json
        
        self.current_json_file = self.get_latest_json_file()
        if not self.current_json_file:
            # If no existing file found, create a new session
            self.create_new_session()
            return
            
        # Извлекаем дату и время из имени JSONL файла
        json_filename = os.path.basename(self.current_json_file)
        match = re.search(r'_(\d{2}_\d{2}_\d{2}_\d{2}_\d{2})\.jsonl$', json_filename)
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
            existing_data = []
            
            # Проверяем расширение файла для определения формата
            if self.current_json_file.endswith('.jsonl'):
                # Читаем JSONL файл построчно
                with open(self.current_json_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:  # Пропускаем пустые строки
                            try:
                                entry = json.loads(line)
                                existing_data.append(entry)
                            except json.JSONDecodeError as je:
                                logging.warning(f"Ignoring invalid JSON on line {line_num}: {str(je)}")
                                continue
            else:
                # Читаем старый JSON файл (массив объектов)
                with open(self.current_json_file, 'r', encoding='utf-8') as f:
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
            
        # Проверка на EAN-13 код (13 цифр)
        if code.isdigit() and len(code) == 13:
            console.print(f"[yellow]Обнаружен EAN-13 код: {code} - обрабатываем как дубликат[/yellow]")
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
        
        # Запускаем все асинхронные операции в одном потоке
        def async_operations():
            # Воспроизводим звук успеха
            self.play_sound(self.sound_success)
            
            # Сохраняем только в JSON (Excel будет создаваться по требованию)
            self.save_json_data(code)
            
            # Проверяем заполнение коробки
            if len(self.current_box) >= box_capacity:
                self.play_sound(self.sound_box_full)
                console.print(Panel.fit(
                    f"[bold red]Коробка {self.box_number} заполнена![/bold red]",
                    border_style="red"
                ))
                self.create_new_box()
        
        # Запускаем все асинхронные операции в отдельном потоке
        threading.Thread(target=async_operations).start()
        
        # Сразу возвращаем результат
        element_number = len(self.current_box)
        console.print(f"[green]Код добавлен в коробку {self.box_number} (элемент {element_number}/{box_capacity}): {code}[/green]")
        return code

    def save_json_data(self, code):
        """Save single code data to JSONL file with append-only writes"""
        import json
        import time
        import threading
        from datetime import datetime
        
        # Используем threading.Lock для синхронизации записи в JSONL
        if not hasattr(self, '_json_lock'):
            self._json_lock = threading.Lock()
        
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self._json_lock:  # Блокируем запись на уровне объекта
                    # Создаем временный lock файл
                    lock_file = f"{self.current_json_file}.lock"
                    
                    try:
                        # Пытаемся создать lock файл (эксклюзивно)
                        with open(lock_file, 'x') as lock_f:
                            lock_f.write(str(os.getpid()))
                    except FileExistsError:
                        # Lock файл уже существует, ждем
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 1.5
                            continue
                        else:
                            raise IOError("JSONL file is locked by another process")
                    
                    try:
                        # Создаем новую запись
                        new_entry = {
                            'Box Number': self.box_number,
                            'Code': code,
                            'Timestamp': datetime.now().isoformat()
                        }
                        
                        # Append-only запись в JSONL файл (одна строка = один JSON объект)
                        with open(self.current_json_file, 'a', encoding='utf-8') as f:
                            json.dump(new_entry, f, ensure_ascii=False)
                            f.write('\n')  # Разделитель строк для JSONL формата
                        
                    finally:
                        # Удаляем lock файл
                        try:
                            os.remove(lock_file)
                        except FileNotFoundError:
                            pass
                
                console.print(f"[blue]Код {code} сохранен в {self.current_json_file}[/blue]")
                return  # Успешно записали, выходим
                
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"[yellow]Попытка {attempt + 1} записи JSONL не удалась: {str(e)}. Повтор через {retry_delay:.2f}с[/yellow]")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    console.print(f"[red]Не удалось сохранить код {code} в JSONL после {max_retries} попыток: {str(e)}[/red]")
                    raise

    def save_box_data(self):
        """Save current box data to Excel file"""
        data = {
            'Box Number': [self.box_number] * len(self.current_box),
            'Code': self.current_box,
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(self.current_box)
        }
        
        df = pd.DataFrame(data)
        
        # Save to Excel with retry mechanism
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Try to acquire file lock
                lock_file = f"{self.current_excel_file}.lock"
                try:
                    with open(lock_file, 'w') as f:
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                except IOError:
                    time.sleep(retry_delay)
                    continue

                try:
                    if os.path.exists(self.current_excel_file):
                        existing_df = pd.read_excel(self.current_excel_file)
                        if not existing_df.empty:
                            # Remove entries for current box if they exist
                            existing_df = existing_df[existing_df['Box Number'] != self.box_number]
                            # Only concatenate if we have data to add
                            if not df.empty:
                                df = pd.concat([existing_df, df], ignore_index=True)
                            else:
                                df = existing_df
                except Exception as e:
                    console.print(f"[yellow]Предупреждение при чтении Excel: {str(e)}[/yellow]")
                    # If we can't read the existing file, we'll just write our new data
                
                df.to_excel(self.current_excel_file, index=False)
                console.print(f"[blue]Данные коробки {self.box_number} сохранены в {self.current_excel_file}[/blue]")
                break  # Success, exit retry loop
                
            except Exception as e:
                if attempt < max_retries - 1:
                    console.print(f"[yellow]Попытка {attempt + 1} из {max_retries} не удалась: {str(e)}[/yellow]")
                    time.sleep(retry_delay)
                else:
                    console.print(f"[red]Не удалось сохранить данные в Excel после {max_retries} попыток: {str(e)}[/red]")
            finally:
                # Release file lock
                try:
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
                except:
                    pass

    def generate_excel_from_json(self):
        """Generate Excel file from current JSONL data"""
        import json
        
        try:
            # Читаем данные из JSON/JSONL файла
            if not os.path.exists(self.current_json_file):
                console.print(f"[red]JSON/JSONL файл не найден: {self.current_json_file}[/red]")
                return False
                
            json_data = []
            
            # Проверяем расширение файла для определения формата
            if self.current_json_file.endswith('.jsonl'):
                # Читаем JSONL файл построчно
                with open(self.current_json_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:  # Пропускаем пустые строки
                            try:
                                entry = json.loads(line)
                                json_data.append(entry)
                            except json.JSONDecodeError as je:
                                logging.warning(f"Ignoring invalid JSON on line {line_num} in generate_excel_from_json: {str(je)}")
                                continue
            else:
                # Читаем старый JSON файл (массив объектов)
                with open(self.current_json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            
            if not json_data:
                console.print("[yellow]JSONL файл пуст, создаем пустой Excel файл[/yellow]")
                df = pd.DataFrame(columns=['Box Number', 'Code', 'Timestamp'])
            else:
                # Конвертируем JSONL данные в DataFrame
                df = pd.DataFrame(json_data)
            
            # Создаем Excel файл (перезаписываем если существует)
            df.to_excel(self.current_excel_file, index=False)
            console.print(f"[green]Excel файл создан: {self.current_excel_file}[/green]")
            console.print(f"[blue]Записано {len(json_data)} записей[/blue]")
            return True
            
        except Exception as e:
            console.print(f"[red]Ошибка при создании Excel файла: {str(e)}[/red]")
            return False

    def create_new_box(self):
        """Create a new box"""
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