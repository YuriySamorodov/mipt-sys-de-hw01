import csv
from datetime import datetime
from pathlib import Path
from typing import Literal

ActionType = Literal['start', 'answer', 'command', 'callback', 'error']

class UserActionLogger:
    """Класс для логирования действий пользователей в CSV-файл с указанием типа действия"""
    
    def __init__(self, log_file: str = 'user_actions.csv'):
        """Инициализация логгера
        
        Args:
            log_file: Путь к файлу для логирования
        """
        self.log_file = Path(log_file)
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Создаёт файл для логирования с заголовками, если он не существует"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'datetime', 'action'])

    def log_action(self, user_id: int, action: ActionType):
        """Записывает действие пользователя в лог-файл
        
        Args:
            user_id: ID пользователя Telegram
            action: Тип действия ('start', 'answer', 'command', 'callback', 'error')
        """
        timestamp = datetime.now().strftime('%d.%m.%Y %H.%M.%S')
        
        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, timestamp, action])
