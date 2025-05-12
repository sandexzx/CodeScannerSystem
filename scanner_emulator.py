import os
import sys
import time
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_output_file():
    # По умолчанию используем scanner_data.txt в текущей директории
    default_file = "scanner_data.txt"
    
    while True:
        file_path = input(f"\nВведите путь к файлу для сохранения кодов (Enter для {default_file}): ").strip()
        if not file_path:
            file_path = default_file
            
        # Если путь не содержит директорий, создаем файл в текущей директории
        if os.path.dirname(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Создаем пустой файл, если он не существует
        with open(file_path, 'a') as f:
            pass
        return file_path

def write_code(file_path, code, codes_buffer=None):
    try:
        with open(file_path, 'a') as f:
            f.write(f"{code}\n")
        
        print(f"\nКод {code} успешно записан в файл")
        return codes_buffer
    except Exception as e:
        print(f"\nОшибка при записи в файл: {e}")
        return codes_buffer

def main():
    clear_screen()
    print("=== Эмулятор сканера штрих-кодов ===")
    
    # Получение пути к файлу
    file_path = get_output_file()
    
    clear_screen()
    print(f"\nЭмулятор запущен!")
    print(f"Формат файла: Одна строка - один код")
    print(f"Файл для записи: {file_path}")
    print("\nВводите коды (для выхода введите 'exit' или нажмите Ctrl+C)")
    print("================================================")
    
    try:
        while True:
            code = input("\nВведите код: ").strip()
            
            if code.lower() == 'exit':
                print("\nЗавершение работы эмулятора...")
                break
                
            if code:
                write_code(file_path, code)
            else:
                print("Код не может быть пустым!")
                
    except KeyboardInterrupt:
        print("\n\nЗавершение работы эмулятора...")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
    finally:
        print("\nЭмулятор остановлен.")

if __name__ == "__main__":
    main() 