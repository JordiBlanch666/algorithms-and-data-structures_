# Author: Jordi Y Blanch
"""
MediaRecover — Deleted image and video recovery for Windows
===========================================================

Requires:
  - Python 3.11+
  - Running as Administrator (raw disk sector access)
  - No external dependencies (standard library only)

Usage:
  python main.py --disk C: --output C:\\Recovered
  python main.py --disk PhysicalDrive0 --output D:\\Recovered --only-images
  python main.py --disk C: --output D:\\Recovered --only-carving
  python main.py --list-disks
"""

import argparse
import ctypes
import logging
import sys
import time
from pathlib import Path

from disk_reader import list_physical_drives, list_logical_volumes
from recovery_engine import RecoveryEngine, RecoveryOptions


# ── Logger ────────────────────────────────────────────────────────────────────
def _setup_logging(verbose: bool):
    level  = logging.DEBUG if verbose else logging.INFO
    fmt    = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%H:%M:%S"
    logging.basicConfig(level=level, format=fmt, datefmt=datefmt,
                        stream=sys.stdout)


# ── Privilege check ───────────────────────────────────────────────────────────
def _check_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# ── Progress bar ──────────────────────────────────────────────────────────────
class ProgressBar:
    def __init__(self, width: int = 50):
        self.width  = width
        self._last  = ""

    def update(self, msg: str, current: int, total: int):
        if total > 0:
            pct  = current / total
            done = int(self.width * pct)
            bar  = "█" * done + "░" * (self.width - done)
            line = f"\r[{bar}] {pct:5.1%}  {msg[:40]:<40}"
        else:
            line = f"\r  ↳ {msg[:70]:<70}"

        if line != self._last:
            print(line, end="", flush=True)
            self._last = line

    def finish(self):
        print()  # new line when done


# ── CLI ───────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mediarecover",
        description="Deep recovery of deleted images and videos (Windows)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --list-disks
  python main.py --disk C: --output D:\\Recovered
  python main.py --disk PhysicalDrive0 --output D:\\Recovered --only-images
  python main.py --disk C: --output D:\\Recovered --only-carving --verbose
""",
    )

    p.add_argument("--list-disks", action="store_true",
                   help="List the available disks and volumes, then exit")

    p.add_argument("--disk", metavar="DISK",
                   help=r"Volume (C:, D:) or physical disk (PhysicalDrive0)")
    p.add_argument("--output", metavar="FOLDER",
                   help="Output folder for the recovered files")

    # Type filters
    grp_type = p.add_mutually_exclusive_group()
    grp_type.add_argument("--only-images", action="store_true",
                          help="Recover images only")
    grp_type.add_argument("--only-videos", action="store_true",
                          help="Recover videos only")

    # Recovery methods
    grp_method = p.add_mutually_exclusive_group()
    grp_method.add_argument("--only-mft", action="store_true",
                             help="Use MFT analysis only (faster, needs NTFS)")
    grp_method.add_argument("--only-carving", action="store_true",
                             help="Use file carving only (slower, works on any file system)")

    # Size options
    p.add_argument("--min-size", type=int, default=10_000, metavar="BYTES",
                   help="Minimum size of files to recover (default: 10,000 bytes)")
    p.add_argument("--max-size", type=int, default=100 * 1024**3, metavar="BYTES",
                   help="Maximum size of files to recover")

    p.add_argument("--hint-path", action="append", metavar="PATH", dest="hint_paths",
                   help="Folder where the files used to be (can be repeated). "
                        "Limits carving to that area of the disk, which is much faster. "
                        "E.g. --hint-path \"C:\\Users\\YourUser\\Videos\"")
    p.add_argument("--hint-user", metavar="USER",
                   help="Automatically adds the given user's Videos, Downloads, Desktop, "
                        "Recycle Bin and Temp folders. "
                        "E.g. --hint-user YourUser")

    p.add_argument("--no-deduplicate", action="store_true",
                   help="Don't remove duplicates (can produce many files)")
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite files that already exist in the output folder")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Show a detailed log")

    return p


def _resolve_disk_path(disk: str) -> str:
    """Normalize the user's input into a valid Win32 path."""
    disk = disk.strip()
    if disk.startswith(r"\\"):
        return disk
    if disk.upper().startswith("PHYSICALDRIVE"):
        return f"\\\\.\\{disk}"
    # Drive letter
    letter = disk.rstrip(":/\\").upper()
    return f"\\\\.\\{letter}:"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = _build_parser()
    args   = parser.parse_args()

    _setup_logging(args.verbose)
    log = logging.getLogger(__name__)

    # ── List disks ───────────────────────────────────────────────────────────
    if args.list_disks:
        print("\n=== Physical disks ===")
        for d in list_physical_drives():
            print(f"  {d}")
        print("\n=== Logical volumes ===")
        for v in list_logical_volumes():
            print(f"  {v}")
        print()
        return

    # ── Validation ───────────────────────────────────────────────────────────
    if not args.disk or not args.output:
        parser.error("--disk and --output are required (or use --list-disks)")

    if not _check_admin():
        print(
            "\n⚠  WARNING: Administrator privileges were not detected.\n"
            "   Raw disk sector access may fail.\n"
            "   Run this script as Administrator for best results.\n"
        )

    disk_path  = _resolve_disk_path(args.disk)
    output_dir = Path(args.output)

    images = not args.only_videos
    videos = not args.only_images

    use_mft     = not args.only_carving
    use_carving = not args.only_mft

    # ── Hint paths for focused carving ──────────────────────────────────────
    hint_paths = list(args.hint_paths) if args.hint_paths else []
    if args.hint_user:
        from cluster_locator import build_hint_paths
        hint_paths.extend(build_hint_paths(args.hint_user))
    hint_paths = hint_paths or None

    # ── Progress setup ───────────────────────────────────────────────────────
    pb = ProgressBar()

    def progress(msg: str, current: int, total: int):
        pb.update(msg, current, total)

    opts = RecoveryOptions(
        disk_path    = disk_path,
        output_dir   = output_dir,
        images       = images,
        videos       = videos,
        use_mft      = use_mft,
        use_carving  = use_carving,
        min_size     = args.min_size,
        max_size     = args.max_size,
        deduplicate  = not args.no_deduplicate,
        overwrite    = args.overwrite,
        hint_paths   = hint_paths,
        progress_cb  = progress,
    )

    print(f"\n{'─'*60}")
    print("  MediaRecover — Image and video recovery")
    print(f"{'─'*60}")
    print(f"  Disk    : {disk_path}")
    print(f"  Output  : {output_dir}")
    print(f"  Types   : {'images ' if images else ''}{'videos' if videos else ''}")
    print(f"  Methods : {'MFT ' if use_mft else ''}{'carving' if use_carving else ''}")
    print(f"{'─'*60}\n")

    t0 = time.time()
    try:
        engine = RecoveryEngine(opts)
        stats  = engine.run()
    except PermissionError as e:
        pb.finish()
        print(f"\n✗ Permission error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        pb.finish()
        print("\n⚠  Recovery interrupted by the user.")
        sys.exit(0)
    finally:
        pb.finish()

    elapsed = time.time() - t0
    print(f"\n{'─'*60}")
    print("  RECOVERY SUMMARY")
    print(f"{'─'*60}")
    print(f"  Found by MFT           : {stats.mft_found:>8,}")
    print(f"  Found by carving       : {stats.carved_found:>8,}")
    print(f"  Files saved            : {stats.saved:>8,}")
    print(f"  Skipped (dupes/size)   : {stats.skipped:>8,}")
    print(f"  Read errors            : {stats.errors:>8,}")
    print(f"  Total time             : {elapsed:>8.1f} s")
    print(f"{'─'*60}")
    print(f"  Files in: {output_dir}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
