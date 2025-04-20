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
    "required_columns": ["id", "timestamp", "action"],
    "time_format": "%Y-%m-%d %H:%M:%S",  # Пример нужного формата для выгрузки в Excel
    "input_time_format": "%d.%m.%Y %H.%M.%S"  # Формат времени в исходном файле
}

def validate_csv(file_path):
    """Проверка структуры CSV файла без заголовков"""
    try:
        df = pd.read_csv(file_path, header=None)
        if df.shape[1] < len(CONFIG['required_columns']):
            raise ValueError(
                f"Недостаточно колонок: найдено {df.shape[1]}, ожидалось минимум {len(CONFIG['required_columns'])}"
            )
        return True
    except pd.errors.EmptyDataError:
        raise ValueError("CSV файл пустой или не содержит данных")
    except Exception as e:
        raise ValueError(f"Ошибка чтения CSV: {str(e)}")

def convert_to_xlsx(csv_path):
    """Конвертация CSV без заголовков в XLSX"""
    try:
        # Чтение без заголовков
        df = pd.read_csv(
            csv_path,
            header=None,
            names=CONFIG['required_columns'],
            dtype={'id': str, 'action': str}
        )

        # Проверка на достаточное количество колонок
        if df.shape[1] < len(CONFIG['required_columns']):
            raise ValueError(f"Недостаточно колонок в данных: найдено {df.shape[1]}, ожидалось {len(CONFIG['required_columns'])}")

        # Обработка временной метки с использованием заданного формата
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format=CONFIG['input_time_format'])
            df['timestamp'] = df['timestamp'].dt.strftime(CONFIG['time_format'])
        except Exception as e:
            raise ValueError(f"Ошибка обработки времени: {str(e)}. Пример значения: {df['timestamp'].iloc[0]}")
        
        # Сохраняем в Excel
        temp_file = Path("temp_stats.xlsx")
        with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='User Actions', index=False)
        
        return temp_file
    except Exception as e:
        print(f"Ошибка конвертации: {str(e)}", file=sys.stderr)
        return None

def upload_to_yandex_disk(local_file, remote_path):
    """Загрузка файла на Яндекс.Диск"""
    try:
        ydisk = YaDisk(token=os.getenv("YANDEX_DISK_TOKEN"))
        
        # Проверка, существует ли путь на Я.Диске
        if not ydisk.exists(remote_path):
            print(f"Указанный путь на Яндекс.Диске не существует: {remote_path}")
            return False
        
        # Открываем файл для чтения
        with open(local_file, 'rb') as file:
            ydisk.upload(file, remote_path)
        
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
        
        # print(f"Проверка файла: {csv_file}")
        # print(f"Размер файла: {csv_file.stat().st_size} байт")
        
        try:
            sample_df = pd.read_csv(csv_file, nrows=2)
            # print("Пример содержимого CSV:")
            # print(sample_df.to_string())
        except Exception as e:
            print(f"Не удалось прочитать CSV для диагностики: {str(e)}")
        
        # Конвертируем CSV в XLSX
        temp_file = convert_to_xlsx(csv_file)
        if not temp_file:
            print(f"Ошибка конвертации CSV в XLSX", file=sys.stderr)
            return 1
        
        # Загружаем файл на Яндекс.Диск
        remote_file_path = os.path.join(CONFIG['remote_path'], CONFIG['remote_filename'])
        if not upload_to_yandex_disk(temp_file, remote_file_path):
            return 1
        
        # Удаляем временный файл после успешной загрузки
        temp_file.unlink()
        print(f"Временный файл удален: {temp_file}")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
