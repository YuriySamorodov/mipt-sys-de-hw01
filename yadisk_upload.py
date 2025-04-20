#!/home/admin0/mipt-sys-de-hw01/venv/bin/python3.12
import os
import pandas as pd
from datetime import datetime
from yadisk import YaDisk
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

CONFIG = {
    "remote_path": "/bot_statistics/",
    "local_file": "user_actions.csv",
    "remote_filename": "user_actions.xlsx",
    "convert_to_excel": True,
    "time_format": "%Y-%m-%d %H:%M:%S"  # Формат временных меток
}

def validate_csv(file_path):
    """Проверяет структуру CSV файла"""
    try:
        df = pd.read_csv(file_path, nrows=1)
        if not {"id", "timestamp", "action"}.issubset(df.columns):
            missing = {"id", "timestamp", "action"} - set(df.columns)
            raise ValueError(f"Отсутствуют обязательные колонки: {missing}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка валидации CSV: {str(e)}")
        return False

def convert_to_xlsx(csv_path):
    """Конвертирует CSV в XLSX с обработкой временных меток"""
    try:
        if not validate_csv(csv_path):
            return None

        df = pd.read_csv(csv_path, usecols=["id", "timestamp", "action"])
        
        # Преобразование временной метки
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['timestamp'] = df['timestamp'].dt.strftime(CONFIG['time_format'])
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка обработки времени: {str(e)}")
            return None
        
        # Создание временного Excel файла
        temp_file = Path("temp_stats.xlsx")
        with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
            # Основной лист с данными
            df.to_excel(writer, sheet_name='User Actions', index=False)
            
            # Лист с агрегированной статистикой по часам
            df['hour'] = pd.to_datetime(df['timestamp']).dt.floor('H')
            hourly_stats = df.groupby(['hour', 'action']).size().unstack(fill_value=0)
            hourly_stats.to_excel(writer, sheet_name='Hourly Stats')
            
        return temp_file
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка конвертации: {str(e)}")
        return None

def ensure_remote_dir(disk, path):
    """Проверяет и создает папку на Яндекс Диске при необходимости"""
    try:
        if not disk.exists(path):
            disk.mkdir(path)
            print(f"[{datetime.now()}] Создана директория: {path}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка работы с директорией: {str(e)}")
        return False

def upload_with_retry(disk, local_path, remote_path, max_attempts=3):
    """Пытается загрузить файл с несколькими попытками"""
    for attempt in range(max_attempts):
        try:
            disk.upload(str(local_path), remote_path, overwrite=True)
            return True
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"[{datetime.now()}] Ошибка загрузки после {max_attempts} попыток: {str(e)}")
                return False
            print(f"[{datetime.now()}] Повторная попытка ({attempt + 1}/{max_attempts})...")
            time.sleep(5 * (attempt + 1))

def upload_file():
    try:
        # Инициализация Яндекс Диска
        disk = YaDisk(token=os.getenv('YANDEX_TOKEN'))
        if not disk.check_token():
            print(f"[{datetime.now()}] Неверный токен Яндекс Диска")
            return

        # Проверка CSV файла
        csv_file = Path(CONFIG['local_file'])
        if not csv_file.exists():
            print(f"[{datetime.now()}] CSV файл не найден: {csv_file}")
            return

        # Конвертация в Excel
        xlsx_file = None
        if CONFIG['convert_to_excel']:
            xlsx_file = convert_to_xlsx(csv_file)
            if not xlsx_file:
                return
            upload_path = xlsx_file
        else:
            upload_path = csv_file

        # Подготовка пути на Яндекс Диске
        remote_path = f"{CONFIG['remote_path'].rstrip('/')}/{CONFIG['remote_filename']}"
        
        # Проверка/создание директории
        if not ensure_remote_dir(disk, CONFIG['remote_path']):
            return

        # Загрузка файла
        if upload_with_retry(disk, upload_path, remote_path):
            print(f"[{datetime.now()}] Файл успешно загружен: {remote_path}")

    except Exception as e:
        print(f"[{datetime.now()}] Критическая ошибка: {str(e)}")
    finally:
        # Удаление временного файла
        if CONFIG['convert_to_excel'] and xlsx_file and xlsx_file.exists():
            xlsx_file.unlink()

if __name__ == "__main__":
    upload_file()
