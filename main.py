import os
import sys
from scanner_handler import start_monitoring
from config import *

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n=== Система учета товаров с отслеживанием файла данных сканера ===")
    print("1. Начать мониторинг файла сканера")
    print("2. Показать текущие настройки")
    print("3. Изменить путь к файлу сканера")
    print("4. Изменить формат файла")
    print("5. Выход")
    print("================================================================")

def show_settings():
    print("\nТекущие настройки:")
    print(f"Путь к файлу сканера: {SCANNER_FILE_PATH}")
    print(f"Формат файла: {FILE_FORMAT}")
    print(f"Вместимость коробки: {BOX_CAPACITY} единиц")
    input("\nНажмите Enter для продолжения...")

def change_scanner_file():
    global SCANNER_FILE_PATH
    new_path = input("\nВведите новый путь к файлу сканера: ").strip()
    if new_path:
        SCANNER_FILE_PATH = new_path
        print(f"Путь к файлу сканера изменен на: {SCANNER_FILE_PATH}")
    input("\nНажмите Enter для продолжения...")

def change_file_format():
    global FILE_FORMAT
    print("\nВыберите формат файла:")
    print("1. Одна строка - один код")
    print("2. CSV (коды через запятую)")
    choice = input("Ваш выбор (1/2): ").strip()
    
    if choice == "1":
        FILE_FORMAT = "single_line"
    elif choice == "2":
        FILE_FORMAT = "csv"
    else:
        print("Неверный выбор!")
        return
        
    print(f"Формат файла изменен на: {FILE_FORMAT}")
    input("\nНажмите Enter для продолжения...")

def main():
    while True:
        clear_screen()
        print_menu()
        
        choice = input("\nВыберите действие (1-5): ").strip()
        
        if choice == "1":
            clear_screen()
            print("Запуск мониторинга файла сканера...")
            print("Для остановки нажмите Ctrl+C")
            start_monitoring()
        elif choice == "2":
            show_settings()
        elif choice == "3":
            change_scanner_file()
        elif choice == "4":
            change_file_format()
        elif choice == "5":
            print("\nЗавершение работы программы...")
            sys.exit(0)
        else:
            print("\nНеверный выбор! Попробуйте снова.")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main() 