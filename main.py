import os
import sys
from scanner_handler import ScannerHandler
from config_manager import load_config, save_config, SCANNER_FILE_PATH
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    console.print(Panel.fit(
        "[bold blue]Система учета товаров с отслеживанием файла данных сканера[/bold blue]",
        border_style="blue"
    ))
    
    table = Table(show_header=False, box=None)
    table.add_row("1", "Начать новую сессию сканирования")
    table.add_row("2", "Продолжить существующую сессию")
    table.add_row("3", "Показать текущие настройки")
    table.add_row("4", "Изменить путь к файлу сканера")
    table.add_row("5", "Изменить вместимость коробки")
    table.add_row("6", "Выход")
    
    console.print(table)

def show_settings():
    config = load_config()
    table = Table(title="Текущие настройки", show_header=True, header_style="bold magenta")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")
    
    table.add_row("Путь к файлу сканера", config['scanner_file_path'])
    table.add_row("Вместимость коробки", str(config['box_capacity']))
    
    console.print(table)
    Prompt.ask("\nНажмите Enter для продолжения")

def change_scanner_file():
    config = load_config()
    new_path = Prompt.ask("\nВведите новый путь к файлу сканера")
    if new_path:
        config["scanner_file_path"] = new_path
        save_config(config)
        console.print(f"[green]Путь к файлу сканера изменен на:[/green] {new_path}")
    Prompt.ask("\nНажмите Enter для продолжения")

def change_box_capacity():
    config = load_config()
    while True:
        try:
            new_capacity = int(Prompt.ask("\nВведите новую вместимость коробки"))
            if new_capacity > 0:
                config["box_capacity"] = new_capacity
                save_config(config)
                console.print(f"[green]Вместимость коробки изменена на:[/green] {new_capacity}")
                break
            else:
                console.print("[red]Вместимость должна быть положительным числом![/red]")
        except ValueError:
            console.print("[red]Пожалуйста, введите корректное число![/red]")
    Prompt.ask("\nНажмите Enter для продолжения")

def main():
    while True:
        clear_screen()
        print_menu()
        
        choice = Prompt.ask("\nВыберите действие", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            clear_screen()
            console.print("[bold blue]Запуск новой сессии сканирования...[/bold blue]")
            handler = ScannerHandler(start_new_session=True)
            handler.start_monitoring()
        elif choice == "2":
            clear_screen()
            console.print("[bold blue]Продолжение существующей сессии...[/bold blue]")
            handler = ScannerHandler(start_new_session=False)
            handler.start_monitoring()
        elif choice == "3":
            show_settings()
        elif choice == "4":
            change_scanner_file()
        elif choice == "5":
            change_box_capacity()
        elif choice == "6":
            if Confirm.ask("\nВы уверены, что хотите выйти?"):
                console.print("\n[yellow]Завершение работы программы...[/yellow]")
                sys.exit(0)
        else:
            console.print("\n[red]Неверный выбор! Попробуйте снова.[/red]")
            Prompt.ask("Нажмите Enter для продолжения")

if __name__ == "__main__":
    main() 