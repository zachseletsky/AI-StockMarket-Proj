"""Use to re-establish data-lake"""

import os

BASE_DIR = "data-lake"
SUBDIRS = [
    "raw/equities",
    "raw/options",
    "raw/fundamentals",
    "raw/news",
    "processed",
    "metadata",
    "logs",
]


def create_directories():
    for sub in SUBDIRS:
        path = os.path.join(BASE_DIR, sub)
        os.makedirs(path, exist_ok=True)
        print(f"[+] Created or verified: {path}")


if __name__ == "__main__":
    create_directories()
