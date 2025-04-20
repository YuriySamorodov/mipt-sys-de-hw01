import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, Optional
import pandas as pd
import uuid

ActionType = Literal['start', 'answer', 'command', 'callback', 'error', 'bot_response']

class UserActionLogger:
    """Логгер действий пользователей с автоматическим определением новых сессий"""
    
    SESSION_TIMEOUT = timedelta(minutes=30)  # Consider new session after 30 minutes of inactivity
    
    def __init__(self, log_file: str = 'user_actions.csv'):
        self.log_file = Path(log_file)
        self._ensure_log_file_exists()
        self.active_sessions = {}  # {user_id: {'session_id': str, 'last_activity': datetime}}

    def _ensure_log_file_exists(self):
        """Создание лог-файла с нужными заголовками"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['user_id', 'session_id', 'datetime', 'action', 'duration'])

    def _get_last_user_action(self, user_id: int) -> Optional[dict]:
        """Возвращает последнее действие пользователя из лога"""
        try:
            df = pd.read_csv(self.log_file)
            user_actions = df[df['user_id'] == user_id]
            if user_actions.empty:
                return None
            return user_actions.iloc[-1].to_dict()
        except Exception:
            return None

    def _should_start_new_session(self, user_id: int, current_time: datetime) -> bool:
        """Определяет, нужно ли начать новую сессию"""
        # No existing session - need new one
        if user_id not in self.active_sessions:
            return True
            
        # Check session timeout
        last_activity = self.active_sessions[user_id]['last_activity']
        if current_time - last_activity > self.SESSION_TIMEOUT:
            return True
            
        # Check if previous action was "end of session" marker
        last_action = self._get_last_user_action(user_id)
        if last_action and last_action.get('action') in ['chat_deleted', 'session_end']:
            return True
            
        return False

    def _update_session_activity(self, user_id: int, current_time: datetime):
        """Обновляет или создает сессию для пользователя"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {
                'session_id': str(uuid.uuid4()),
                'last_activity': current_time
            }
        else:
            self.active_sessions[user_id]['last_activity'] = current_time

    def log_action(self, user_id: int, action: ActionType, is_session_end: bool = False):
        """Запись действия в лог с автоматическим управлением сессиями
        
        Args:
            user_id: ID пользователя
            action: Тип действия
            is_session_end: Явно отмечает конец сессии (например, при удалении чата)
        """
        now = datetime.now()
        now_str = now.strftime('%d.%m.%Y %H.%M.%S')

        # Handle session logic
        if self._should_start_new_session(user_id, now) or action == 'start' or is_session_end:
            self.active_sessions.pop(user_id, None)  # Clear existing session
        
        self._update_session_activity(user_id, now)
        session_id = self.active_sessions[user_id]['session_id']

        # Calculate duration since last action in THIS session
        duration = 0.0
        last_action = self._get_last_user_action(user_id)
        
        if last_action and last_action.get('session_id') == session_id:
            try:
                last_dt = datetime.strptime(last_action['datetime'], '%d.%m.%Y %H.%M.%S')
                duration = (now - last_dt).total_seconds()
            except Exception:
                pass

        # Log the action
        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, session_id, now_str, action, round(duration, 2)])

        # Explicit session end handling
        if is_session_end:
            self.active_sessions.pop(user_id, None)
