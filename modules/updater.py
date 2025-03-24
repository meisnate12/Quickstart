import os
import sys
import shutil
import zipfile
import tempfile
import requests
from pathlib import Path
from modules import helpers

UPDATE_URL_TEMPLATE = "https://github.com/Kometa-Team/Quickstart/archive/refs/heads/{branch}.zip"
APP_ROOT = Path(__file__).resolve().parents[1]

class Updater:
    def __init__(self):
        self.branch = helpers.get_branch()
        self.version_info = helpers.check_for_update()
        self.temp_dir = Path(tempfile.gettempdir()) / "quickstart-update"
        self.backup_dir = APP_ROOT / "backup"


    def update_available(self):
        return self.version_info.get("update_available", False)


    def get_update_url(self):
        return UPDATE_URL_TEMPLATE.format(branch=self.branch)


    def download_package(self):
        url = self.get_update_url()
        response = requests.get(url, stream=True)
        response.raise_for_status()

        zip_path = self.temp_dir / "update.zip"
        os.makedirs(self.temp_dir, exist_ok=True)

        with open(zip_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        return zip_path


    def unpack_package(self, zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.temp_dir)
        extracted_folder = next(self.temp_dir.glob("Quickstart-*"))
        return extracted_folder


    def backup_current_version(self):
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        shutil.copytree(APP_ROOT, self.backup_dir, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'flask_session', 'uploads', 'previews'))


    def replace_with_new_version(self, new_dir):
        for item in new_dir.iterdir():
            dest = APP_ROOT / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)


    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


    def apply_update(self, dry_run=False):
        if not self.update_available():
            print("No update available.")
            return

        print("[INFO] Starting update...")
        try:
            zip_file = self.download_package()
            new_files = self.unpack_package(zip_file)
            self.backup_current_version()
            print(f"[DRY RUN] Would replace files in: {APP_ROOT}")
            if not dry_run:
                self.replace_with_new_version(new_files)
                print("[INFO] Files replaced.")
            else:
                print("[DRY RUN] File replacement skipped.")
            print("[INFO] Update process completed.")
        finally:
            self.cleanup()
