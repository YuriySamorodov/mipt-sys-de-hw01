#!/home/admin0/mipt-sys-de-hw01/venv/bin/python3.12
import os
import pandas as pd
from datetime import datetime
from yadisk import YaDisk
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "remote_path": "/bot_statistics/",  # Must end with /
    "local_file": "user_actions.csv",
    "convert_to_excel": True
}

def convert_to_xlsx(csv_path):
    xlsx_path = csv_path.with_suffix('.xlsx')
    try:
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        return xlsx_path
    except Exception as e:
        print(f"[{datetime.now()}] Conversion error: {str(e)}")
        return None

def ensure_remote_dir(disk, path):
    """Ensure remote directory exists, create if needed"""
    try:
        if not disk.exists(path):
            disk.mkdir(path)
            print(f"[{datetime.now()}] Created remote directory: {path}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Directory creation failed: {str(e)}")
        return False

def upload_file():
    try:
        disk = YaDisk(token=os.getenv('YANDEX_TOKEN'))
        
        if not disk.check_token():
            print(f"[{datetime.now()}] Invalid token")
            return

        # Verify/create remote directory
        if not ensure_remote_dir(disk, CONFIG['remote_path']):
            return

        csv_file = Path(CONFIG['local_file'])
        if not csv_file.exists():
            print(f"[{datetime.now()}] CSV file not found")
            return

        upload_path = csv_file
        if CONFIG['convert_to_excel']:
            if xlsx_file := convert_to_xlsx(csv_file):
                upload_path = xlsx_file

        remote_name = f"stats_{datetime.now().strftime('%Y%m%d_%H%M')}{upload_path.suffix}"
        remote_path = f"{CONFIG['remote_path'].rstrip('/')}/{remote_name}"

        # Upload file
        disk.upload(str(upload_path), remote_path)
        print(f"[{datetime.now()}] Successfully uploaded to {remote_path}")

        # Cleanup temporary file
        if CONFIG['convert_to_excel'] and upload_path.suffix == '.xlsx':
            upload_path.unlink()

    except Exception as e:
        print(f"[{datetime.now()}] Upload failed: {str(e)}")

if __name__ == "__main__":
    upload_file()
