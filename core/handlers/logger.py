import csv
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import pandas as pd

ActionType = Literal['start', 'answer', 'command', 'callback', 'error', 'bot_response']

class UserActionLogger:
    """Класс для логирования действий пользователей в CSV-файл с расширенными метаданными"""
    
    def __init__(self, log_file: str = 'user_actions.csv', session_timeout: int = 30 * 60):
        self.log_file = Path(log_file)
        self.session_timeout = session_timeout
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Создаёт файл с заголовками, если он не существует"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'id', 'datetime', 'action', 
                    'duration', 'session_id', 
                    'platform', 'response_time'
                ])

    def _get_last_user_action(self, user_id: int) -> Optional[dict]:
        """Возвращает последнюю запись пользователя из CSV"""
        try:
            df = pd.read_csv(self.log_file)
            df = df[df['id'] == user_id]
            if df.empty:
                return None
            last_row = df.iloc[-1]
            return last_row.to_dict()
        except Exception:
            return None

    def _infer_platform(self, user_agent: Optional[str]) -> str:
        """Примитивное определение платформы по user_agent"""
        if not user_agent:
            return "unknown"
        ua = user_agent.lower()
        if 'android' in ua:
            return 'android'
        elif 'iphone' in ua or 'ios' in ua:
            return 'ios'
        elif 'windows' in ua:
            return 'windows'
        elif 'mac' in ua:
            return 'mac'
        else:
            return 'other'

    def log_action(self, user_id: int, action: ActionType, user_agent: Optional[str] = None):
        """Записывает действие пользователя в лог с дополнительными полями"""
        now = datetime.now()
        now_str = now.strftime('%d.%m.%Y %H.%M.%S')
        platform = self._infer_platform(user_agent)

        last_action = self._get_last_user_action(user_id)
        
        # Вычисляем duration
        if last_action:
            last_time = datetime.strptime(last_action['datetime'], '%d.%m.%Y %H.%M.%S')
            duration = (now - last_time).total_seconds()
            new_session = duration > self.session_timeout
            session_id = int(last_action['session_id']) + 1 if new_session else int(last_action['session_id'])
        else:
            duration = 0
            session_id = 1

        # Для response_time: если текущее действие — bot_response, и до этого был запрос
        response_time = None
        if last_action and action == 'bot_response' and last_action['action'] in ['start', 'command', 'answer', 'callback']:
            response_time = duration
        elif action != 'bot_response':
            response_time = None

        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                user_id, now_str, action,
                round(duration, 2), session_id,
                platform, round(response_time, 2) if response_time is not None else ''
            ])
