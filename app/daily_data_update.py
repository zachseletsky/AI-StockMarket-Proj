"""
Used as a single entry point to update all data daily
"""

import subprocess
from pathlib import Path


def refresh_data() -> bool:
    method_path = Path("app/update_raw_data.py")
    try:
        subprocess.run(["python", method_path], check=True)
    except Exception as e:
        print("Error: \n" + str(e))
        return False
    return True


def sync_data_lake() -> bool:
    method_path = Path("scripts/backup_to_icloud.py")
    try:
        subprocess.run(["python", method_path], check=True)
    except Exception as e:
        print("Error: \n" + str(e))
        return False
    return True


def main() -> bool:
    success = refresh_data()
    if success:
        success = sync_data_lake()
        if not success:
            print("Backup Canceled due to previous error")
    return success


if __name__ == "__main__":
    main()
