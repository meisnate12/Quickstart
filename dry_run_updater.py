from modules.updater import Updater

if __name__ == "__main__":
    updater = Updater()
    if updater.update_available():
        print(f"Update available: {updater.version_info['remote_version']}")
        updater.apply_update(dry_run=True)
    else:
        print("No update available.")
