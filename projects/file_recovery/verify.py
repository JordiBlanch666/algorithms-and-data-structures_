# Author: Jordi Y Blanch
"""
Quick checker for recovered video files.
Analyzes their internal structure without needing VLC or ffmpeg.
Reports which ones have a real chance of playing.
"""
import struct
import sys
import os
import logging
from pathlib import Path
from dataclasses import dataclass

log = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm",
                    ".mpg", ".mpeg", ".vob", ".flv", ".wmv", ".3gp",
                    ".mts", ".m2ts"}

# ── Per-format checkers ──────────────────────────────────────────────────────

def _verify_mp4(data: bytes) -> tuple[bool, str]:
    pos = 0
    has_ftyp = has_moov = has_mdat = False
    while pos + 8 <= len(data):
        size = struct.unpack_from(">I", data, pos)[0]
        btype = data[pos+4:pos+8]
        if size == 0:
            break
        if size == 1:
            if pos + 16 > len(data):
                break
            size = struct.unpack_from(">Q", data, pos+8)[0]
        if btype == b"ftyp": has_ftyp = True
        if btype == b"moov": has_moov = True
        if btype == b"mdat": has_mdat = True
        if size < 8:
            break
        pos += size

    if has_moov and has_mdat:
        note = "✓ moov + mdat present"
        if not has_ftyp:
            note += " (no ftyp — may need repair)"
        return True, note
    if has_mdat and not has_moov:
        return False, "✗ moov missing (interrupted recording)"
    if not has_mdat:
        return False, "✗ mdat missing (no video data)"
    return False, "✗ incomplete structure"


def _verify_avi(data: bytes) -> tuple[bool, str]:
    if data[:4] != b"RIFF" or data[8:12] != b"AVI ":
        return False, "✗ invalid RIFF/AVI signature"
    has_movi = b"LIST" in data[:4096] or b"movi" in data
    has_idx1 = b"idx1" in data
    if has_movi:
        note = "✓ valid RIFF structure"
        if not has_idx1:
            note += " (no idx1 — may need repair)"
        return True, note
    return False, "✗ movi block not found"


def _verify_mkv(data: bytes) -> tuple[bool, str]:
    if data[:4] != b"\x1A\x45\xDF\xA3":
        return False, "✗ invalid EBML signature"
    has_segment = b"\x18\x53\x80\x67" in data[:256]
    has_cluster = b"\x1F\x43\xB6\x75" in data
    if has_cluster:
        return True, "✓ valid EBML with data clusters"
    if has_segment:
        return False, "✗ segment present but no clusters (no data)"
    return False, "✗ incomplete EBML structure"


def _verify_mpg(data: bytes) -> tuple[bool, str]:
    pack_count = data.count(b"\x00\x00\x01\xBA")
    seq_count  = data.count(b"\x00\x00\x01\xB3")
    if pack_count >= 10:
        return True, f"✓ {pack_count} pack headers, {seq_count} sequence headers"
    if pack_count >= 2:
        return False, f"⚠ only {pack_count} packs — possibly incomplete"
    if seq_count >= 1:
        return False, f"⚠ MPEG-1 with {seq_count} sequence headers but few packs"
    return False, "✗ no valid MPEG packets found"


def _verify_flv(data: bytes) -> tuple[bool, str]:
    if data[:3] != b"FLV":
        return False, "✗ invalid FLV signature"
    return True, "✓ valid FLV signature"


def _verify_wmv(data: bytes) -> tuple[bool, str]:
    if data[:8] != b"\x30\x26\xB2\x75\x8E\x66\xCF\x11":
        return False, "✗ invalid ASF/WMV signature"
    return True, "✓ valid ASF/WMV signature"


def _verify_mts(data: bytes) -> tuple[bool, str]:
    # Check for a 0x47 sync byte every 188 bytes (at least 10 packets)
    if len(data) < 188 * 10:
        return False, "✗ file too small for MTS"
    valid_syncs = sum(1 for i in range(10) if data[i * 188] == 0x47)
    if valid_syncs >= 8:
        return True, f"✓ valid MPEG-TS ({valid_syncs}/10 correct sync bytes)"
    return False, f"✗ MTS false positive ({valid_syncs}/10 sync bytes) — not real AVCHD"


VERIFIERS = {
    ".mp4": _verify_mp4, ".mov": _verify_mp4, ".m4v": _verify_mp4,
    ".3gp": _verify_mp4,
    ".avi": _verify_avi,
    ".mkv": _verify_mkv, ".webm": _verify_mkv,
    ".mpg": _verify_mpg, ".mpeg": _verify_mpg, ".vob": _verify_mpg,
    ".flv": _verify_flv,
    ".wmv": _verify_wmv,
    ".mts": _verify_mts, ".m2ts": _verify_mts,
}

PROBE_SIZE = 5 * 1024 * 1024   # read only the first 5 MB to check


# ── Result ────────────────────────────────────────────────────────────────────
@dataclass
class VerifyResult:
    path: Path
    size_mb: float
    viable: bool
    note: str

    def line(self) -> str:
        icon = "✓" if self.viable else "✗"
        return f"  {icon}  {self.size_mb:6.1f} MB  {self.path.name:<45}  {self.note}"


# ── Main logic ───────────────────────────────────────────────────────────────
def verify_file(path: Path) -> VerifyResult:
    ext = path.suffix.lower()
    size_mb = path.stat().st_size / (1024 * 1024)

    if ext not in VERIFIERS:
        return VerifyResult(path, size_mb, False, "unsupported format")

    try:
        with open(path, "rb") as f:
            data = f.read(PROBE_SIZE)
    except OSError as e:
        return VerifyResult(path, size_mb, False, f"read error: {e}")

    if len(data) < 16:
        return VerifyResult(path, size_mb, False, "✗ file too small")

    viable, note = VERIFIERS[ext](data)
    return VerifyResult(path, size_mb, viable, note)


def verify_folder(folder: Path) -> list[VerifyResult]:
    files = sorted(
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    )
    return [verify_file(f) for f in files]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    p = argparse.ArgumentParser(
        prog="verify",
        description="Checks which recovered video files are playable",
    )
    p.add_argument("input", help="File or folder to check")
    p.add_argument("--viable-only", action="store_true",
                   help="Show only the viable files")
    p.add_argument("--copy-viable", metavar="DEST",
                   help="Copy the viable files to this folder")
    args = p.parse_args()

    target = Path(args.input)
    if not target.exists():
        print(f"✗ Not found: {target}")
        sys.exit(1)

    print(f"\nAnalyzing: {target}\n")

    if target.is_file():
        results = [verify_file(target)]
    else:
        results = verify_folder(target)

    if not results:
        print("No video files found.")
        return

    viables  = [r for r in results if r.viable]
    invalids = [r for r in results if not r.viable]

    print(f"{'─'*80}")
    print(f"  {'MB':>6}  {'File':<45}  Result")
    print(f"{'─'*80}")

    if not args.viable_only:
        for r in invalids:
            print(r.line())

    for r in viables:
        print(r.line())

    print(f"{'─'*80}")
    print(f"  Total: {len(results)}  |  Viable: {len(viables)}  |  Corrupted: {len(invalids)}")
    print(f"{'─'*80}\n")

    if args.copy_viable and viables:
        import shutil
        dest = Path(args.copy_viable)
        dest.mkdir(parents=True, exist_ok=True)
        for r in viables:
            shutil.copy2(r.path, dest / r.path.name)
        print(f"  {len(viables)} viable file(s) copied to: {dest}\n")


if __name__ == "__main__":
    main()
