# Система учета товаров с отслеживанием файла данных сканера

Система для автоматического учета товаров с использованием сканера штрих-кодов и мониторинга файла данных.

## Требования

- Python 3.9 или выше
- Установленные зависимости из requirements.txt

## Установка

1. Клонируйте репозиторий или распакуйте архив
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Создайте звуковые файлы в директории `sounds`:
   - success.wav - звук успешного сканирования
   - error.wav - звук ошибки (дубликат)
   - box_full.wav - звук заполнения коробки

2. Настройте параметры в файле `config.py`:
   - SCANNER_FILE_PATH - путь к файлу, куда сканер записывает данные
   - FILE_FORMAT - формат файла ("single_line" или "csv")
   - BOX_CAPACITY - вместимость коробки (по умолчанию 12 единиц)

## Использование

1. Запустите программу:
```bash
python main.py
```

2. В главном меню выберите нужное действие:
   - Начать мониторинг файла сканера
   - Показать текущие настройки
   - Изменить путь к файлу сканера
   - Изменить формат файла
   - Выход

3. При запуске мониторинга:
   - Программа будет отслеживать изменения в файле сканера
   - При сканировании кода будет воспроизводиться звуковой сигнал
   - При обнаружении дубликата будет воспроизводиться звук ошибки
   - При заполнении коробки будет воспроизводиться специальный сигнал
   - Данные о коробках сохраняются в Excel-файл в директории export

## Форматы файла сканера

1. Одна строка - один код:
```
123456789
987654321
```

2. CSV (коды через запятую):
```
123456789,987654321,456789123
```

## Логирование

Все действия системы записываются в файл `scanner.log` с временными метками.

## Экспорт данных

Данные о коробках и их содержимом автоматически экспортируются в Excel-файл в директории `export/boxes.xlsx`. 