import os
import sys
import time
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_file_format():
    while True:
        clear_screen()
        print("\n=== Эмулятор сканера штрих-кодов ===")
        print("Выберите формат файла:")
        print("1. Одна строка - один код")
        print("2. CSV (коды через запятую)")
        choice = input("\nВаш выбор (1/2): ").strip()
        
        if choice == "1":
            return "single_line"
        elif choice == "2":
            return "csv"
        else:
            print("\nНеверный выбор! Попробуйте снова.")
            time.sleep(1)

def get_output_file():
    while True:
        file_path = input("\nВведите путь к файлу для сохранения кодов: ").strip()
        if file_path:
            # Если путь не содержит директорий, создаем файл в текущей директории
            if os.path.dirname(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Создаем пустой файл, если он не существует
            with open(file_path, 'a') as f:
                pass
            return file_path
        print("Путь не может быть пустым!")

def write_code(file_path, code, file_format, codes_buffer=None):
    try:
        if file_format == "single_line":
            with open(file_path, 'a') as f:
                f.write(f"{code}\n")
        else:  # csv format
            if codes_buffer is None:
                codes_buffer = []
            codes_buffer.append(code)
            
            with open(file_path, 'w') as f:
                f.write(','.join(codes_buffer))
        
        print(f"\nКод {code} успешно записан в файл")
        return codes_buffer
    except Exception as e:
        print(f"\nОшибка при записи в файл: {e}")
        return codes_buffer

def main():
    clear_screen()
    print("=== Эмулятор сканера штрих-кодов ===")
    
    # Выбор формата файла
    file_format = select_file_format()
    
    # Получение пути к файлу
    file_path = get_output_file()
    
    # Буфер для CSV формата
    codes_buffer = [] if file_format == "csv" else None
    
    clear_screen()
    print(f"\nЭмулятор запущен!")
    print(f"Формат файла: {'Одна строка - один код' if file_format == 'single_line' else 'CSV'}")
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
                codes_buffer = write_code(file_path, code, file_format, codes_buffer)
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