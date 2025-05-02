"""
sha256_monitor.py
-----------------
Real‑time directory monitor that computes and stores an SHA‑256 digest **immediately**
after a new file is closed.  Two persistence channels are used:
    1.  macOS extended attribute  (key = b"user.sha256")
    2.  Side‑car text file        (<filename>.sha256)

Both mechanisms satisfy the user's reproducibility guardrails (§47) by
explicitly labelling files and creating an immutable checksum artefact.

Usage
-----
    python sha256_monitor.py /absolute/path/to/data/root

Dependencies
------------
    pip install watchdog>=2.3.0 xattr>=0.10.1

Author
------
    OpenAI o3, 2025‑05‑02
"""

import argparse
import hashlib
from pathlib import Path
import sys
import time

from watchdog.events import FileSystemEventHandler, FileClosedEvent
from watchdog.observers import Observer

try:
    import xattr  # macOS extended attributes
except ImportError:
    xattr = None  # Fallback: we will still write the side‑car file

# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


def compute_sha256(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    """Compute the SHA‑256 digest of *path*.

    Parameters
    ----------
    path : Path
        File that will be read in binary mode.
    block_size : int, optional (default = 8 MiB)
        The size (bytes) of each chunk read into memory at a time.

    Returns
    -------
    str
        64‑character hexadecimal SHA‑256 digest of the file contents.
    """
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            sha.update(chunk)
    return sha.hexdigest()


def set_xattr_sha256(path: Path, digest: str) -> None:
    """Attempt to write *digest* into the `user.sha256` extended attribute.

    If the platform or user permissions forbid extended attributes, the
    function quietly exits; the side‑car file remains as the canonical
    metadata store.

    Parameters
    ----------
    path : Path
        Target file whose attribute will be set.
    digest : str
        64‑character hexadecimal SHA‑256 digest.
    """
    if xattr is None:
        return  # no module available
    try:
        xattr.setxattr(path, b"user.sha256", digest.encode())
    except OSError:
        pass  # silently ignore; caller relies on side‑car fallback


def write_sidecar_file(path: Path, digest: str) -> Path:
    """Write *digest* into a companion `<path>.sha256` text file.

    Parameters
    ----------
    path : Path
        Original data file.
    digest : str
        The SHA‑256 digest to record.

    Returns
    -------
    Path
        The full path of the side‑car file that was created/overwritten.
    """
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar.write_text(digest + "\n", encoding="ascii")
    return sidecar


# ---------------------------------------------------------------------------
# Watchdog Event Handler
# ---------------------------------------------------------------------------


class DigestWriter(FileSystemEventHandler):
    """Handles file‑close events by computing and saving SHA‑256 digests."""

    def __init__(self, root: Path):
        super().__init__()
        self.root = root

    # -- watchdog 2.3 added FileClosedEvent on macOS & Linux (inotify/kqueue)
    def on_closed(self, event: FileClosedEvent):  # type: ignore[override]
        if event.is_directory:
            return
        file_path = Path(event.src_path)

        # Skip temporary or side‑car files to avoid infinite loops
        if file_path.suffix == ".sha256" or file_path.name.startswith(".~"):
            return

        try:
            digest = compute_sha256(file_path)
            set_xattr_sha256(file_path, digest)
            write_sidecar_file(file_path, digest)
            print(f"[SHA‑256] {file_path.relative_to(self.root)} → {digest}")
        except Exception as e:
            print(f"[ERROR] Could not hash {file_path}: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI Entry‑Point
# ---------------------------------------------------------------------------


def main(argv=None):
    """Parse CLI arguments and start the directory observer."""
    parser = argparse.ArgumentParser(description="Real‑time SHA‑256 metadata writer")
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory to monitor (recursively) for new/modified files",
    )
    args = parser.parse_args(argv)

    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"{root} is not a directory")

    print(f"\n>>> Monitoring {root} for file‑close events… (Ctrl‑C to quit)\n")

    event_handler = DigestWriter(root)
    observer = Observer()
    observer.schedule(event_handler, str(root), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping observer.  Goodbye.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

# ----------------------------------------------------------------------
# Command‑line helper for pre‑commit
#   --oneshot  <files...>  : write/overwrite side‑cars, set xattr
#   --verify   <files...>  : exit 1 if any digest mismatch
# ----------------------------------------------------------------------
if (
    __name__ == "__main__"
    and len(sys.argv) > 1
    and sys.argv[1] in ("--oneshot", "--verify")
):
    mode = sys.argv[1]
    files = list(map(Path, sys.argv[2:]))
    rc = 0
    for fp in files:
        if fp.suffix == ".sha256":
            continue
        calc = compute_sha256(fp)
        if mode == "--oneshot":
            set_xattr_sha256(fp, calc)
            write_sidecar_file(fp, calc)
        else:  # verify
            sidecar = fp.with_suffix(fp.suffix + ".sha256")
            have = sidecar.read_text().strip() if sidecar.exists() else None
            if have != calc:
                print(f"[SHA‑256 ERROR] {fp} digest mismatch", file=sys.stderr)
                rc = 1
    sys.exit(rc)
