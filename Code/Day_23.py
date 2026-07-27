#---------------------------------
# you need to install watchdog first
# python -m pip install watchdog
#---------------------------------


import argparse
import logging
import shutil
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

RULES = {
    ".jpg": "Images",  ".jpeg": "Images", ".png": "Images",
    ".gif": "Images",  ".webp": "Images", ".svg": "Images",
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents",
    ".xlsx": "Documents", ".pptx": "Documents", ".txt": "Documents",
    ".py":  "Code",    ".js":  "Code",    ".ts":  "Code",
    ".html":"Code",    ".css": "Code",    ".json":"Code",
    ".zip": "Archives",".tar": "Archives",".gz":  "Archives",
    ".rar": "Archives",
    ".mp3": "Audio",   ".wav": "Audio",   ".flac":"Audio",
    ".mp4": "Video",   ".mov": "Video",   ".mkv": "Video",
}
MISC_FOLDER  = "Misc"
SKIP_SUFFIXES = {".tmp", ".crdownload", ".part", ".ds_store"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("organiser")

def get_destination(path: Path, rules: dict) -> str:
    suffix = path.suffix.lower()
    if suffix in SKIP_SUFFIXES:
        return None
    return rules.get(suffix, MISC_FOLDER)

def safe_move(src: Path, dest_dir: Path, dry_run: bool = False) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
        counter += 1

    if dry_run:
        log.info(f"[DRY RUN] Would move: {src.name} → {dest_dir.name}/")
        return dest

    shutil.move(str(src), str(dest))
    log.info(f"Moved: {src.name} → {dest_dir.name}/")
    return dest

def organise_existing(watch_dir: Path, rules: dict, dry_run: bool = False):
    files = [p for p in watch_dir.iterdir()
             if p.is_file() and not p.name.startswith(".")]
    if not files:
        log.info("No existing files to organise.")
        return

    log.info(f"Organising {len(files)} existing file(s)...")
    moved = 0
    for f in files:
        folder_name = get_destination(f, rules)
        if folder_name is None:
            continue
        dest_dir = watch_dir / folder_name
        
        if f.parent != watch_dir:
            continue
        safe_move(f, dest_dir, dry_run=dry_run)
        moved += 1

    log.info(f"Done — {moved} file(s) {'would be ' if dry_run else ''}moved.")

class OrganiserHandler(FileSystemEventHandler):
    def __init__(self, watch_dir: Path, rules: dict, dry_run: bool = False):
        self.watch_dir = watch_dir
        self.rules     = rules
        self.dry_run   = dry_run
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return

        src = Path(event.src_path)

        
        if src.name.startswith(".") or src.suffix.lower() in SKIP_SUFFIXES:
            return

        
        time.sleep(0.5)
        if not src.exists():
            return

        folder_name = get_destination(src, self.rules)
        if folder_name is None:
            return

        dest_dir = self.watch_dir / folder_name
        safe_move(src, dest_dir, dry_run=self.dry_run)

    def on_moved(self, event):
        
        if event.is_directory:
            return
        dest_path = Path(event.dest_path)
        if dest_path.parent != self.watch_dir:
            return
        self.on_created(type("E", (), {"src_path": str(dest_path),
                                        "is_directory": False})())
        
def start_watcher(watch_dir: Path, rules: dict, dry_run: bool = False):
    handler  = OrganiserHandler(watch_dir, rules, dry_run)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    mode = " [DRY RUN]" if dry_run else ""
    log.info(f"Watching: {watch_dir}{mode}  (Ctrl+C to stop)")

    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping watcher...")
    finally:
        observer.stop()
        observer.join()
        log.info("Watcher stopped.")

def build_parser():
    parser = argparse.ArgumentParser(
        description="Auto-organise files by extension."
    )
    parser.add_argument(
        "watch_dir", nargs="?", default=".",
        help="Directory to watch (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without moving files"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Organise existing files then exit (no watcher)"
    )
    return parser

def main():
    parser    = build_parser()
    args      = parser.parse_args()
    watch_dir = Path(args.watch_dir).resolve()

    if not watch_dir.exists():
        print(f"Directory not found: {watch_dir}")
        return

    log.info(f"Target directory: {watch_dir}")

    if args.clean:
        organise_existing(watch_dir, RULES, dry_run=args.dry_run)
        return

    
    organise_existing(watch_dir, RULES, dry_run=args.dry_run)
    start_watcher(watch_dir, RULES, dry_run=args.dry_run)

if __name__ == "__main__":
    main()



