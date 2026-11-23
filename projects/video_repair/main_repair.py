# Author: Jordi Y Blanch
"""
VideoRepair — Corrupted video repairer (pure Python, no dependencies)
=====================================================================

Supported formats: MP4, MOV, M4V, AVI, MKV, WebM, MPG, MPEG, VOB

Usage:
  python main_repair.py --input video.mp4 --output repaired/
  python main_repair.py --input corrupted_folder/ --output repaired/
  python main_repair.py --diagnose video.mp4
"""
import argparse
import logging
import sys
from pathlib import Path

from repair_engine import RepairEngine, SUPPORTED
from mp4_repair import diagnose as diagnose_mp4
from avi_repair import diagnose as diagnose_avi
from mkv_repair import diagnose as diagnose_mkv
from mpg_repair import diagnose as diagnose_mpg
from utils import human_size


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


DIAGNOSERS = {
    ".mp4": diagnose_mp4, ".m4v": diagnose_mp4, ".mov": diagnose_mp4,
    ".avi": diagnose_avi,
    ".mkv": diagnose_mkv, ".webm": diagnose_mkv,
    ".mpg": diagnose_mpg, ".mpeg": diagnose_mpg, ".vob": diagnose_mpg,
}


def _run_diagnose(path: Path):
    ext = path.suffix.lower()
    if ext not in DIAGNOSERS:
        print(f"✗ Unsupported format: {ext}")
        return

    info = DIAGNOSERS[ext](path)
    issues = info.get("issues", [])
    size   = info.get("file_size", 0)

    print(f"\n{'─'*55}")
    print(f"  Diagnosis: {path.name}")
    print(f"{'─'*55}")
    print(f"  Size      : {human_size(size)}")
    print(f"  Format    : {ext.lstrip('.')}")

    if not issues:
        print("  Status    : ✓ No problems found")
    else:
        print(f"  Problems  : {len(issues)}")
        for issue in issues:
            print(f"    • {_issue_description(issue)}")
    print(f"{'─'*55}\n")


def _issue_description(issue: str) -> str:
    descriptions = {
        "ftyp_missing":         "The ftyp atom (file type) is missing",
        "moov_missing":         "The moov atom (metadata) is missing — interrupted recording",
        "moov_corrupted_size":  "The moov atom has the wrong size",
        "moov_after_mdat":      "The moov atom is at the end (can cause slow loading)",
        "mdat_missing":         "The mdat block (video data) is missing",
        "truncated":            "The file looks truncated (incomplete)",
        "riff_size_wrong":      "Wrong RIFF size in the header",
        "idx1_missing":         "The idx1 index is missing (AVI not seekable)",
        "idx1_empty":           "The idx1 index is empty",
        "not_riff":             "Not a valid RIFF file",
        "not_avi":              "The RIFF container does not hold AVI",
        "not_ebml":             "No EBML header found (MKV/WebM)",
        "segment_missing":      "No EBML Segment found",
        "segment_size_unknown": "The Segment has an unknown size (normal for streams)",
        "seekhead_missing":     "The SeekHead is missing (MKV not seekable)",
        "cues_missing":         "The Cues are missing (degraded seeking)",
        "info_missing":         "The Info element is missing",
        "too_small":            "The file is too small to be valid",
        "unsupported_format":   "Unsupported file format",
    }
    return descriptions.get(issue, issue)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="videorepair",
        description="Corrupted video repairer — MP4, AVI, MKV, MPG (pure Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_repair.py --diagnose video.mp4
  python main_repair.py --input video.mp4 --output C:\\Repaired
  python main_repair.py --input C:\\Recovered --output C:\\Repaired
  python main_repair.py --input folder/ --output repaired/ --verbose
""",
    )

    p.add_argument("--diagnose", metavar="FILE",
                   help="Analyze a file and show problems without repairing it")
    p.add_argument("--input", "-i", metavar="FILE_OR_FOLDER",
                   help="File or folder with videos to repair")
    p.add_argument("--output", "-o", metavar="FOLDER",
                   help="Folder where the repaired videos are saved")
    p.add_argument("--no-backup", action="store_true",
                   help="Don't create a .bak copy of the original file")
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite the repaired file if it already exists")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Show a detailed log")
    return p


def main():
    parser = _build_parser()
    args   = parser.parse_args()
    _setup_logging(args.verbose)

    # ── Diagnosis mode ────────────────────────────────────────────────────────
    if args.diagnose:
        _run_diagnose(Path(args.diagnose))
        return

    # ── Repair mode ────────────────────────────────────────────────────────────
    if not args.input or not args.output:
        parser.error("--input and --output are required (or use --diagnose)")

    src = Path(args.input)
    dst = Path(args.output)

    if not src.exists():
        print(f"✗ Not found: {src}")
        sys.exit(1)

    engine = RepairEngine(
        output_dir = dst,
        backup     = not args.no_backup,
        overwrite  = args.overwrite,
    )

    print(f"\n{'─'*55}")
    print("  VideoRepair — Video repairer")
    print(f"{'─'*55}")
    print(f"  Input   : {src}")
    print(f"  Output  : {dst}")
    print(f"  Formats : {', '.join(SUPPORTED)}")
    print(f"{'─'*55}\n")

    results = engine.repair_all(src)

    ok      = [r for r in results if r.success]
    failed  = [r for r in results if not r.success]
    no_issues = [r for r in ok if not r.issues]

    print(f"\n{'─'*55}")
    print("  SUMMARY")
    print(f"{'─'*55}")
    print(f"  Files processed     : {len(results):>5}")
    print(f"  No problems         : {len(no_issues):>5}")
    print(f"  Repaired            : {len(ok) - len(no_issues):>5}")
    print(f"  Not repairable      : {len(failed):>5}")
    print(f"{'─'*55}")

    if failed:
        print("\n  Files that could not be repaired:")
        for r in failed:
            print(f"    • {r.src.name}: {r.error}")

    print(f"\n  Files saved to: {dst}\n")


if __name__ == "__main__":
    main()
