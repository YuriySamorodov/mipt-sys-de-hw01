#!/home/admin0/mipt-sys-de-hw01/venv/bin/python3.12
import os
import json
from datetime import datetime
from yadisk import YaDisk
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config" / "upload_config.json"

class ConfigLoader:
    @staticmethod
    def load():
        with open(CONFIG_PATH) as f:
            return json.load(f)

class YandexUploader:
    def __init__(self):
        self.config = ConfigLoader.load()
        self.disk = YaDisk(
            id=os.getenv('YANDEX_APP_ID'),
            secret=os.getenv('YANDEX_APP_SECRET'),
            token=os.getenv('YANDEX_TOKEN')
        )
        
    def upload(self):
        stats_file = Path("user_actions.csv")
        if not stats_file.exists():
            print(f"[{datetime.now()}] No statistics file found")
            return

        remote_name = f"stats_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        remote_path = f"{self.config['remote_path']}/{remote_name}"
        
        try:
            self.disk.upload(str(stats_file), remote_path)
            print(f"[{datetime.now()}] Uploaded {remote_name}")
            
            if self.config.get('datalens_integration', False):
                self.notify_datalens(remote_path)
                
        except Exception as e:
            print(f"[{datetime.now()}] Upload failed: {str(e)}")

    def notify_datalens(self, remote_path):
        """Placeholder for Datalens integration"""
        print(f"[{datetime.now()}] Datalens notified about {remote_path}")

if __name__ == "__main__":
    uploader = YandexUploader()
    uploader.upload()
