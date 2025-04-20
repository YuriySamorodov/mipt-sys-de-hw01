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
    "remote_path": "/bot_statistics/",  # папка на Яндекс Диске
    "local_file": "user_actions.csv",  # Локальный csv файл
    "remote_filename": "user_actions.xlsx", 
    "convert_to_excel": True
}

def convert_to_xlsx(csv_path):
    """ Ковертирует CSV в XLSX"""
    try:
        df = pd.read_csv(csv_path)
        # Create in-memory Excel file
        with pd.ExcelWriter("temp.xlsx", engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return Path("temp.xlsx")
    except Exception as e:
        print(f"[{datetime.now()}] Conversion error: {str(e)}")
        return None

def ensure_remote_dir(disk, path):
    """Проверяет наличие папки на Яндекс Диске"""
    try:
        if not disk.exists(path):
            disk.mkdir(path)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Directory error: {str(e)}")
        return False

def upload_file():
    try:
        disk = YaDisk(token=os.getenv('YANDEX_TOKEN'))
        
        if not disk.check_token():
            print(f"[{datetime.now()}] Invalid token")
            return

        # Проверяет папку на Яндекс Диске
        if not ensure_remote_dir(disk, CONFIG['remote_path']):
            return

        # Проверяет, что исходный файл никуда не исчез
        csv_file = Path(CONFIG['local_file'])
        if not csv_file.exists():
            print(f"[{datetime.now()}] CSV file not found")
            return

        # Конвертирует CSV в XSLX, если необходимо
        upload_path = csv_file
        if CONFIG['convert_to_excel']:
            if xlsx_file := convert_to_xlsx(csv_file):
                upload_path = xlsx_file

        # Полный путь на Яндекс Диске
        remote_path = f"{CONFIG['remote_path'].rstrip('/')}/{CONFIG['remote_filename']}"

        # Загрузка на Яндекс Диск с перезаписью
        for attempt in range(3):
            try:
                disk.upload(
                    str(upload_path), 
                    remote_path,
                    overwrite=True  # This enables file overwriting
                )
                print(f"[{datetime.now()}] Successfully updated {remote_path}")
                break
            except Exception as e:
                if attempt == 2:
                    print(f"[{datetime.now()}] Final upload failed: {str(e)}")
                else:
                    print(f"[{datetime.now()}] Retrying upload... ({attempt+1}/3)")
                    time.sleep(2)

        # Очистка временных файлов
        if CONFIG['convert_to_excel'] and upload_path.exists() and upload_path.name == "temp.xlsx":
            upload_path.unlink()

    except Exception as e:
        print(f"[{datetime.now()}] Critical error: {str(e)}")

if __name__ == "__main__":
    upload_file()
