"""
  Backs up datalake instance to icloud where there is plenty of
  already-paid for cloud data

"""


import shutil
from pathlib import Path

# Path to your local data-lake folder inside the GitHub repo
data_lake_src = Path("data-lake")

# Path to your iCloud Drive folder where the backup will be stored
icloud_dst = Path(
    "/Users/zachseletsky/Library/Mobile Documents/com~apple~CloudDocs/data-lake"
)


def copy_data_lake():
    if not data_lake_src.exists():
        print(f"[ERROR] Source folder does not exist: {data_lake_src}")
        return

    if icloud_dst.exists():
        print(f"[INFO] Removing old backup at {icloud_dst}")
        shutil.rmtree(icloud_dst)

    print(f"[INFO] Copying {data_lake_src} to {icloud_dst}")
    shutil.copytree(data_lake_src, icloud_dst)
    print("[SUCCESS] Backup completed.")


def download_data_lake():
    if not icloud_dst.exists():
        print(f"[ERROR] iCloud data-lake folder does not exist: {icloud_dst}")
        return

    if data_lake_src.exists():
        print(f"[INFO] Archiving current data-lake at {data_lake_src}")
        shutil.make_archive("data-lake-archive", "zip", "data-lake")

    print(f"[INFO] Copying {icloud_dst} to {data_lake_src}")
    shutil.copytree(icloud_dst, data_lake_src)
    print("[SUCCESS] Download completed.")


if __name__ == "__main__":
    copy_data_lake()
