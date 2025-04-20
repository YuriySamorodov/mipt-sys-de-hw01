#!/home/admin0/mipt-sys-de-hw01/venv/bin/python3.12
import os
import pandas as pd
from datetime import datetime
from yadisk import YaDisk
from pathlib import Path
from dotenv import load_dotenv
import time
import sys

load_dotenv()

CONFIG = {
    "remote_path": "/bot_statistics/",
    "local_file": "user_actions.csv",
    "remote_filename": "user_actions.xlsx",
    "convert_to_excel": True,
    "required_columns": ["user_id", "session_id", "datetime", "action", "duration"],
    "time_format": "%Y-%m-%d %H:%M:%S",
    "input_time_format": "%d.%m.%Y %H.%M.%S"
}

def validate_csv(file_path):
    """Проверка структуры CSV файла"""
    try:
        df = pd.read_csv(file_path)
        if not all(col in df.columns for col in CONFIG['required_columns']):
            raise ValueError(
                f"Не хватает обязательных колонок. Найдено: {df.columns.tolist()}, ожидалось: {CONFIG['required_columns']}"
            )
        return True
    except pd.errors.EmptyDataError:
        raise ValueError("CSV файл пустой или не содержит данных")
    except Exception as e:
        raise ValueError(f"Ошибка чтения CSV: {str(e)}")

def convert_to_xlsx(csv_path):
    """Конвертация CSV в XLSX с правильной обработкой времени"""
    try:
        # Чтение CSV с заголовками
        df = pd.read_csv(
            csv_path,
            dtype={'user_id': str, 'session_id': str, 'action': str}
        )

        # Проверка обязательных колонок
        missing_cols = [col for col in CONFIG['required_columns'] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_cols}")

        # Обработка временной метки
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], format=CONFIG['input_time_format'])
            df['datetime'] = df['datetime'].dt.strftime(CONFIG['time_format'])
        except Exception as e:
            raise ValueError(f"Ошибка обработки времени: {str(e)}. Пример значения: {df['datetime'].iloc[0]}")
        
        # Сохраняем в Excel
        temp_file = Path("temp_stats.xlsx")
        with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='User Actions', index=False)
        
        return temp_file
    except Exception as e:
        print(f"Ошибка конвертации: {str(e)}", file=sys.stderr)
        return None

def upload_to_yandex_disk(local_file, remote_path):
    """Загрузка файла на Яндекс.Диск с перезаписью существующего файла"""
    try:
        ydisk = YaDisk(token=os.getenv("YANDEX_TOKEN"))
        
        with open(local_file, 'rb') as file:
            ydisk.upload(file, remote_path, overwrite=True)
        
        print(f"Файл успешно загружен на Яндекс.Диск")
        return True
    except Exception as e:
        print(f"Ошибка загрузки на Яндекс.Диск: {str(e)}", file=sys.stderr)
        return False

def main():
    try:
        csv_file = Path(CONFIG['local_file'])
        if not csv_file.exists():
            print(f"Файл не найден: {csv_file}", file=sys.stderr)
            return 1
        
        # Валидация CSV
        try:
            validate_csv(csv_file)
        except Exception as e:
            print(f"Ошибка валидации CSV: {str(e)}", file=sys.stderr)
            return 1
        
        # Конвертация
        temp_file = convert_to_xlsx(csv_file)
        if not temp_file:
            return 1
        
        # Загрузка на Яндекс.Диск
        remote_file_path = os.path.join(CONFIG['remote_path'], CONFIG['remote_filename'])
        if not upload_to_yandex_disk(temp_file, remote_file_path):
            return 1
        
        # Удаление временного файла
        temp_file.unlink()
        print(f"Временный файл удален: {temp_file}")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
