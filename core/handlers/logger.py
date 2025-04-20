import csv
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import pandas as pd

ActionType = Literal['start', 'answer', 'command', 'callback', 'error', 'bot_response']

class UserActionLogger:
    """Логгер действий пользователей с вычислением duration между событиями"""
    
    def __init__(self, log_file: str = 'user_actions.csv'):
        self.log_file = Path(log_file)
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Создание лог-файла с нужными заголовками"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'datetime', 'action', 'duration'])

    def _get_last_user_action(self, user_id: int) -> Optional[str]:
        """Возвращает дату-время последнего действия пользователя"""
        try:
            df = pd.read_csv(self.log_file)
            df = df[df['id'] == user_id]
            if df.empty:
                return None
            return df.iloc[-1]['datetime']
        except Exception:
            return None

    def log_action(self, user_id: int, action: ActionType):
        """Запись действия в лог с вычислением времени между событиями"""
        now = datetime.now()
        now_str = now.strftime('%d.%m.%Y %H.%M.%S')

        duration = 0.0
        last_datetime_str = self._get_last_user_action(user_id)
        if last_datetime_str:
            try:
                last_dt = datetime.strptime(last_datetime_str, '%d.%m.%Y %H.%M.%S')
                duration = (now - last_dt).total_seconds()
            except Exception:
                pass

        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, now_str, action, round(duration, 2)])
