"""
Простой отладочный скрипт для ручной отправки Excel через SMTP с подробным выводом.
Запустите в корне проекта (там, где находятся backend/config.json).

Использование:
  python backend/debug_send_email.py [--file path_to_excel]

Если --file не указан, будет использован путь из config.json: export_file

Скрипт включает smtplib debug output (server.set_debuglevel(1)) и печатает полный traceback в случае ошибки.
"""
import sys
import os
import argparse
import mimetypes
import smtplib
import traceback
from email.message import EmailMessage

# Сохраняем исходную рабочую директорию и загружаем конфиг из backend/config.json по абсолютному пути.
# Это позволяет вызывать скрипт из корня проекта с относительными путями к файлам.
original_cwd = os.getcwd()
script_dir = os.path.abspath(os.path.dirname(__file__))

from importlib import util
# Загружаем config_manager из backend напрямую, не полагаясь на текущую рабочую директорию
spec = util.spec_from_file_location("config_manager", os.path.join(script_dir, "config_manager.py"))
config_manager = util.module_from_spec(spec)
spec.loader.exec_module(config_manager)
load_config = config_manager.load_config

def mask(s: str):
    if not s:
        return ""
    return s[0] + "*" * (len(s)-2) + s[-1] if len(s) > 2 else "*" * len(s)

def main():
    parser = argparse.ArgumentParser(description="Debug send excel via SMTP using config.json")
    parser.add_argument('--file', '-f', help='Path to Excel file to attach (optional)')
    args = parser.parse_args()

    cfg = load_config()
    excel_path = args.file or cfg.get('export_file')

    print("Используемые настройки (частично скрыт пароль):")
    print(" smtp_host:", cfg.get('smtp_host'))
    print(" smtp_port:", cfg.get('smtp_port'))
    print(" smtp_username:", cfg.get('smtp_username'))
    print(" smtp_password:", mask(cfg.get('smtp_password') or ""))
    print(" smtp_use_tls:", cfg.get('smtp_use_tls'))
    print(" mail_from:", cfg.get('mail_from'))
    print(" mail_to:", cfg.get('mail_to'))
    print(" excel_path (raw):", excel_path)
    print()

    # Resolve excel_path robustly: try as given, absolute, joined with project root, joined with backend dir
    candidates = []
    try:
        cwd = os.getcwd()
    except Exception:
        cwd = ""
    # As provided
    candidates.append(excel_path)
    # Absolute / normalized
    candidates.append(os.path.abspath(excel_path))
    candidates.append(os.path.normpath(excel_path))
    # Joined with current working dir
    if cwd:
        candidates.append(os.path.join(cwd, excel_path))
    # Joined with script directory (backend)
    candidates.append(os.path.join(script_dir, excel_path))
    # If the config file itself used a relative path from backend, try joining backend to that
    try:
        cfg_export = cfg.get('export_file') or ""
        if cfg_export and not os.path.isabs(cfg_export):
            candidates.append(os.path.join(script_dir, cfg_export))
            candidates.append(os.path.join(cwd, cfg_export))
    except Exception:
        pass

    # Deduplicate while preserving order
    seen = set()
    resolved_candidates = []
    for p in candidates:
        try:
            np = os.path.normpath(p) if p else p
        except Exception:
            np = p
        if np and np not in seen:
            seen.add(np)
            resolved_candidates.append(np)

    found_path = None
    print("Пробуем найти файл по путям:")
    for p in resolved_candidates:
        print("  -", p)
        try:
            if p and os.path.exists(p):
                found_path = p
                break
        except Exception:
            continue

    if not found_path:
        print("ERROR: Excel-файл не найден. Попробуйте указать --file с абсолютным путем или проверьте export_file в config.json.")
        sys.exit(2)

    # Use the resolved absolute path
    excel_path = os.path.abspath(found_path)
    print("Используем файл:", excel_path)

    # prepare message
    msg = EmailMessage()
    msg['Subject'] = 'Debug: Exported Excel from CodeScannerSystem'
    msg['From'] = cfg.get('mail_from') or ''
    msg['To'] = cfg.get('mail_to') or ''
    msg.set_content('Тестовое письмо с вложением Excel (debug).')

    ctype, _ = mimetypes.guess_type(excel_path)
    if ctype is None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    try:
        with open(excel_path, 'rb') as f:
            data = f.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(excel_path))
    except Exception as e:
        print("Ошибка при чтении файла:", e)
        traceback.print_exc()
        sys.exit(3)

    host = cfg.get('smtp_host') or ''
    port = int(cfg.get('smtp_port') or 0)
    username = cfg.get('smtp_username') or ''
    password = cfg.get('smtp_password') or ''
    use_tls = bool(cfg.get('smtp_use_tls', True))

    if not host or not port or not msg['From'] or not msg['To']:
        print("ERROR: не заданы обязательные настройки SMTP (host/port/from/to).")
        sys.exit(4)

    print("Попытка подключения к SMTP серверу...")
    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            server = smtplib.SMTP(host, port, timeout=20)
            server.set_debuglevel(1)  # Включаем smtplib debug output
            server.ehlo()
            if use_tls:
                print("Включаем STARTTLS...")
                server.starttls()
                server.ehlo()

        if username:
            print("Логинимся как:", username)
            server.login(username, password)

        print("Отправка сообщения...")
        server.send_message(msg)
        print("Письмо успешно отправлено.")
        try:
            server.quit()
        except Exception:
            pass

    except Exception as e:
        print("Ошибка при отправке письма:", str(e))
        print("Полный traceback:")
        traceback.print_exc()
        try:
            server.quit()
        except Exception:
            pass
        sys.exit(5)

if __name__ == '__main__':
    main()
