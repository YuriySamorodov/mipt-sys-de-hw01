import csv
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import pandas as pd
import uuid

ActionType = Literal['start', 'answer', 'command', 'callback', 'error', 'bot_response']

class UserActionLogger:
    """Логгер действий пользователей с вычислением duration между событиями и поддержкой session_id"""
    
    def __init__(self, log_file: str = 'user_actions.csv'):
        self.log_file = Path(log_file)
        self._ensure_log_file_exists()
        self.active_sessions = {}  # Stores active sessions: {user_id: session_id}

    def _ensure_log_file_exists(self):
        """Создание лог-файла с нужными заголовками"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'session_id', 'datetime', 'action', 'duration'])

    def _get_last_user_action(self, user_id: int) -> Optional[tuple[str, str]]:
        """Возвращает (дату-время, session_id) последнего действия пользователя"""
        try:
            df = pd.read_csv(self.log_file)
            df = df[df['id'] == user_id]
            if df.empty:
                return None, None
            return df.iloc[-1]['datetime'], df.iloc[-1]['session_id']
        except Exception:
            return None, None

    def _get_or_create_session(self, user_id: int) -> str:
        """Получает текущую сессию или создает новую"""
        if user_id not in self.active_sessions:
            # Create new session ID
            self.active_sessions[user_id] = str(uuid.uuid4())
        return self.active_sessions[user_id]

    def log_action(self, user_id: int, action: ActionType, new_session: bool = False):
        """Запись действия в лог с вычислением времени между событиями
        
        Args:
            user_id: ID пользователя
            action: Тип действия
            new_session: Принудительно начать новую сессию
        """
        now = datetime.now()
        now_str = now.strftime('%d.%m.%Y %H.%M.%S')

        # Handle session
        if new_session or action == 'start':
            self.active_sessions.pop(user_id, None)  # Clear existing session if any
        session_id = self._get_or_create_session(user_id)

        # Calculate duration
        duration = 0.0
        last_datetime_str, last_session_id = self._get_last_user_action(user_id)
        
        if last_datetime_str and last_session_id == session_id:  # Only calculate duration within same session
            try:
                last_dt = datetime.strptime(last_datetime_str, '%d.%m.%Y %H.%M.%S')
                duration = (now - last_dt).total_seconds()
            except Exception:
                pass

        # Log the action
        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, session_id, now_str, action, round(duration, 2)])
