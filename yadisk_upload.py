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
    "time_format": "%Y-%m-%d %H:%M:%S"
}

def validate_csv(file_path):
    """Тщательная проверка структуры CSV файла"""
    try:
        df = pd.read_csv(file_path, nrows=0)
        actual_columns = [col.strip().lower() for col in df.columns]
        required_columns = [col.strip().lower() for col in CONFIG['required_columns']]
        
        missing = [col for col in required_columns if col not in actual_columns]
        if missing:
            actual_cols_str = ", ".join(df.columns) if len(df.columns) > 0 else "нет колонок"
            raise ValueError(
                f"Отсутствуют обязательные колонки: {missing}\n"
                f"Фактические колонки в файле: {actual_cols_str}\n"
                f"Ожидаемые колонки: {CONFIG['required_columns']}"
            )
        
        return True
    except pd.errors.EmptyDataError:
        raise ValueError("CSV файл пустой или не содержит данных")
    except Exception as e:
        raise ValueError(f"Ошибка чтения CSV: {str(e)}")

def convert_to_xlsx(csv_path):
    """Конвертация CSV в XLSX с улучшенной обработкой ошибок"""
    try:
        validate_csv(csv_path)
        
        df = pd.read_csv(
            csv_path,
            usecols=CONFIG['required_columns'],
            dtype={'id': str, 'action': str}
        )
        df.columns = df.columns.str.strip().str.lower()
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['timestamp'] = df['timestamp'].dt.strftime(CONFIG['time_format'])
        except Exception as e:
            raise ValueError(f"Ошибка
