import os
import sys
from scanner_handler import ScannerHandler
from config_manager import load_config, save_config, SCANNER_FILE_PATH

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n=== Система учета товаров с отслеживанием файла данных сканера ===")
    print("1. Начать новую сессию сканирования")
    print("2. Продолжить существующую сессию")
    print("3. Показать текущие настройки")
    print("4. Изменить путь к файлу сканера")
    print("5. Изменить вместимость коробки")
    print("6. Выход")
    print("================================================================")

def show_settings():
    config = load_config()
    print("\nТекущие настройки:")
    print(f"Путь к файлу сканера: {config['scanner_file_path']}")
    print(f"Вместимость коробки: {config['box_capacity']} единиц")
    input("\nНажмите Enter для продолжения...")

def change_scanner_file():
    config = load_config()
    new_path = input("\nВведите новый путь к файлу сканера: ").strip()
    if new_path:
        config["scanner_file_path"] = new_path
        save_config(config)
        print(f"Путь к файлу сканера изменен на: {new_path}")
    input("\nНажмите Enter для продолжения...")

def change_box_capacity():
    config = load_config()
    while True:
        try:
            new_capacity = int(input("\nВведите новую вместимость коробки: ").strip())
            if new_capacity > 0:
                config["box_capacity"] = new_capacity
                save_config(config)
                print(f"Вместимость коробки изменена на: {new_capacity}")
                break
            else:
                print("Вместимость должна быть положительным числом!")
        except ValueError:
            print("Пожалуйста, введите корректное число!")
    input("\nНажмите Enter для продолжения...")

def main():
    while True:
        clear_screen()
        print_menu()
        
        choice = input("\nВыберите действие (1-6): ").strip()
        
        if choice == "1":
            clear_screen()
            print("Запуск новой сессии сканирования...")
            print("Для остановки нажмите Ctrl+C")
            handler = ScannerHandler(start_new_session=True)
            handler.start_monitoring()
        elif choice == "2":
            clear_screen()
            print("Продолжение существующей сессии...")
            print("Для остановки нажмите Ctrl+C")
            handler = ScannerHandler(start_new_session=False)
            handler.start_monitoring()
        elif choice == "3":
            show_settings()
        elif choice == "4":
            change_scanner_file()
        elif choice == "5":
            change_box_capacity()
        elif choice == "6":
            print("\nЗавершение работы программы...")
            sys.exit(0)
        else:
            print("\nНеверный выбор! Попробуйте снова.")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main() 