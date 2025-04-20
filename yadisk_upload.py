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
    "convert_to_excel": True
}

def convert_to_xlsx(csv_path):
    """Конвертирует CSV в XLSX с обработкой временных меток"""
    try:
        # Чтение CSV с указанием нужных столбцов
        df = pd.read_csv(csv_path, usecols=["id", "timestamp, GMT", "action"])
        
        # Переименование столбца для удобства
        df = df.rename(columns={"timestamp, GMT": "timestamp"})
        
        # Преобразование временной метки
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Создание Excel файла
        with pd.ExcelWriter("temp.xlsx", engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            # Добавляем лист с агрегированной статистикой по часам
            df['hour'] = df['timestamp'].dt.floor('H')
            hourly_stats = df.groupby(['hour', 'action']).size().unstack(fill_value=0)
            hourly_stats.to_excel(writer, sheet_name='Hourly Stats')
            
        return Path("temp.xlsx")
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка конвертации: {str(e)}")
        return None

def ensure_remote_dir(disk, path):
    """Проверяет наличие папки на Яндекс Диске"""
    try:
        if not disk.exists(path):
            disk.mkdir(path)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка при работе с директорией: {str(e)}")
        return False

def upload_file():
    try:
        disk = YaDisk(token=os.getenv('YANDEX_TOKEN'))
        
        if not disk.check_token():
            print(f"[{datetime.now()}] Неверный токен")
            return

        # Проверяем папку на Яндекс Диске
        if not ensure_remote_dir(disk, CONFIG['remote_path']):
            return

        # Проверяем наличие исходного файла
        csv_file = Path(CONFIG['local_file'])
        if not csv_file.exists():
            print(f"[{datetime.now()}] CSV файл не найден")
            return

        # Конвертируем в XLSX
        upload_path = csv_file
        if CONFIG['convert_to_excel']:
            if xlsx_file := convert_to_xlsx(csv_file):
                upload_path = xlsx_file
            else:
                return

        # Формируем путь на Яндекс Диске
        remote_path = f"{CONFIG['remote_path'].rstrip('/')}/{CONFIG['remote_filename']}"

        # Загружаем с 3 попытками
        for attempt in range(3):
            try:
                disk.upload(
                    str(upload_path), 
                    remote_path,
                    overwrite=True
                )
                print(f"[{datetime.now()}] Файл успешно обновлен: {remote_path}")
                break
            except Exception as e:
                if attempt == 2:
                    print(f"[{datetime.now()}] Ошибка загрузки после 3 попыток: {str(e)}")
                else:
                    print(f"[{datetime.now()}] Повторная попытка ({attempt+1}/3)...")
                    time.sleep(2)

        # Удаляем временный файл
        if CONFIG['convert_to_excel'] and upload_path.name == "temp.xlsx":
            upload_path.unlink()

    except Exception as e:
        print(f"[{datetime.now()}] Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    upload_file()
