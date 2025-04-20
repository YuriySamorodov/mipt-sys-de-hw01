#!/home/admin0/mipt-sys-de-hw01/venv/bin/python3.12
import os
import pandas as pd
from datetime import datetime
from yadisk import YaDisk
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

CONFIG = {
    "remote_path": "/bot_statistics/",
    "local_file": "user_actions.csv",
    "convert_to_excel": True
}

def convert_to_xlsx(csv_path):
    """Конвертирует CSV в XLSX"""
    xlsx_path = csv_path.with_suffix('.xlsx')
    try:
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False)
        return xlsx_path
    except Exception as e:
        print(f"Ошибка конвертации: {str(e)}")
        return None

def upload_file():
    disk = YaDisk(token=os.getenv('YANDEX_TOKEN'))
    csv_file = Path(CONFIG['local_file'])
    
    if not csv_file.exists():
        print(f"[{datetime.now()}] CSV файл не найден")
        return

    # Конвертация в XLSX если требуется
    upload_file = csv_file
    if CONFIG['convert_to_excel']:
        if xlsx_file := convert_to_xlsx(csv_file):
            upload_file = xlsx_file
        else:
            return

    # Загрузка на Яндекс.Диск
    remote_name = f"stats_{datetime.now().strftime('%Y%m%d_%H%M')}{upload_file.suffix}"
    remote_path = f"{CONFIG['remote_path']}{remote_name}"
    
    try:
        disk.upload(upload_file, remote_path)
        print(f"[{datetime.now()}] Файл {remote_name} успешно загружен")
        
        # Удаляем временный XLSX файл
        if CONFIG['convert_to_excel'] and upload_file.suffix == '.xlsx':
            upload_file.unlink()
            
    except Exception as e:
        print(f"[{datetime.now()}] Ошибка загрузки: {str(e)}")

if __name__ == "__main__":
    upload_file()
