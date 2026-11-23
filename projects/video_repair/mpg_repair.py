# Author: Jordi Y Blanch
"""
Repairer for MPEG-1 / MPEG-2 files (.mpg, .mpeg, .vob).

Fixes:
  1. Replaces corrupted packs with valid null packs
  2. Skips leading bytes before the first Pack header
  3. Removes garbage bytes between packets
  4. Truncates the file at the last valid packet
"""
import struct
import logging
from pathlib import Path

from utils import CorruptionError, human_size

log = logging.getLogger(__name__)

# MPEG-2 PS packet start signatures
PACK_START  = b"\x00\x00\x01\xBA"   # Pack header
VIDEO_START = b"\x00\x00\x01\xB3"   # Sequence header (MPEG-1 video)
PES_STARTS  = {0xE0, 0xE1, 0xE2, 0xE3,  # video streams
               0xC0, 0xC1, 0xC2, 0xC3,  # audio streams
               0xBD, 0xBE, 0xBF}         # private / padding

# MPEG-2 PS null pack (valid 2048-byte padding)
NULL_PACK = PACK_START + b"\x00" * 2044


def _is_pack_header(data: bytes, pos: int) -> bool:
    if pos + 4 > len(data):
        return False
    return data[pos:pos+4] == PACK_START


def _is_pes_header(data: bytes, pos: int) -> bool:
    if pos + 4 > len(data):
        return False
    if data[pos:pos+3] != b"\x00\x00\x01":
        return False
    return data[pos+3] in PES_STARTS


def _next_sync(data: bytes, pos: int) -> int:
    """Find the next Pack or PES header from pos. Returns -1 if there is none."""
    while pos + 4 <= len(data):
        if data[pos:pos+3] == b"\x00\x00\x01":
            if data[pos+3] == 0xBA or data[pos+3] in PES_STARTS:
                return pos
        pos += 1
    return -1


def _read_pes_size(data: bytes, pos: int) -> int:
    """Return the total size of the PES packet (header + payload)."""
    if pos + 6 > len(data):
        return 0
    payload_len = struct.unpack_from(">H", data, pos + 4)[0]
    return 6 + payload_len if payload_len > 0 else 0


def _find_real_end(data: bytes) -> int:
    """
    Find the real offset where the valid MPEG content ends.
    Looks for the 0x000001B9 end code or the last pack followed by zeros/garbage.
    """
    # Case 1: explicit end code
    end_code = data.rfind(b"\x00\x00\x01\xB9")
    if end_code != -1 and end_code > len(data) // 2:
        return end_code + 4

    # Case 2: find the last valid pack followed by an area with no packs.
    # Scan the tail of the file for the last PACK_START
    # followed by at least 12 coherent bytes
    search_window = min(len(data), 50 * 1024 * 1024)  # search the last 50 MB
    tail = data[len(data) - search_window:]
    tail_offset = len(data) - search_window

    last_valid = -1
    pos = 0
    while pos < len(tail) - 4:
        idx = tail.find(PACK_START, pos)
        if idx == -1:
            break
        # Check that the next sync is within 2 MB (a reasonable packet)
        next_sync = tail.find(b"\x00\x00\x01", idx + 4)
        if next_sync != -1 and next_sync - idx < 2 * 1024 * 1024:
            last_valid = tail_offset + next_sync
        pos = idx + 4

    return last_valid if last_valid > len(data) // 4 else len(data)


def diagnose(path: Path) -> dict:
    data   = path.read_bytes()
    issues = []

    if len(data) < 12:
        return {"issues": ["too_small"], "file_size": len(data)}

    if data[:4] not in (PACK_START, VIDEO_START):
        if b"\x00\x00\x01\xBA" not in data[:2048]:
            issues.append("no_mpeg_signature")

    pack_count = data.count(PACK_START)
    if pack_count == 0:
        issues.append("no_pack_headers")
    elif pack_count < 3:
        issues.append("very_few_packs")

    # Detect a garbage tail (carved file with no known end)
    real_end = _find_real_end(data)
    if real_end < len(data) - 1024:
        issues.append(f"garbage_tail_{len(data) - real_end}_bytes")

    # Check whether it ends abruptly
    last_pack = data.rfind(PACK_START)
    if last_pack != -1 and last_pack > len(data) - 12:
        issues.append("truncated")

    return {"issues": issues, "file_size": len(data),
            "pack_count": pack_count, "real_end": real_end}


def repair(src: Path, dst: Path) -> list[str]:
    data  = src.read_bytes()
    fixes: list[str] = []

    # ── 1. Find the first valid sync ──────────────────────────────────────────
    first_sync = _next_sync(data, 0)
    if first_sync == -1:
        raise CorruptionError("No valid MPEG packets were found.")

    if first_sync > 0:
        data  = data[first_sync:]
        fixes.append(f"stripped_{first_sync}_bytes_before_first_sync")

    # ── 2. Rebuild the stream, dropping corrupted areas ──────────────────────
    output  = bytearray()
    pos     = 0
    good    = 0
    skipped = 0

    while pos < len(data):
        if _is_pack_header(data, pos):
            # 2048-byte pack (DVD sector) or variable size
            # Try to read up to the next pack
            next_pos = _next_sync(data, pos + 4)
            if next_pos == -1:
                # Last packet — copy through to the end
                output += data[pos:]
                good += 1
                break

            chunk = data[pos:next_pos]
            # Make sure the chunk isn't too big (>= 1 MB = garbage)
            if len(chunk) <= 1024 * 1024:
                output += chunk
                good += 1
            else:
                # Large corrupted area → insert a null pack and skip it
                output += NULL_PACK
                skipped += 1

            pos = next_pos

        elif _is_pes_header(data, pos):
            size = _read_pes_size(data, pos)
            if size > 0 and pos + size <= len(data):
                output += data[pos:pos+size]
                good += 1
                pos  += size
            else:
                pos += 1

        else:
            # Garbage byte → skip it
            pos += 1
            skipped += 1

    if good == 0:
        raise CorruptionError("No recoverable packets were found.")

    fixes.append(f"reconstructed_{good}_packets")
    if skipped:
        fixes.append(f"skipped_{skipped}_corrupt_bytes")

    # ── 3. Add the MPEG end code if it's missing ─────────────────────────────
    if not bytes(output).endswith(b"\x00\x00\x01\xB9"):
        output += b"\x00\x00\x01\xB9"
        fixes.append("end_code_added")

    dst.write_bytes(bytes(output))
    return fixes


def repair_mpg(src: Path, dst: Path) -> dict:
    info   = diagnose(src)
    issues = info["issues"]
    real_end = info.get("real_end", src.stat().st_size)

    # If the only problem is a garbage tail, just truncate it
    garbage_issues = [i for i in issues if i.startswith("garbage_tail")]
    other_issues   = [i for i in issues if not i.startswith("garbage_tail")]

    if garbage_issues and not other_issues:
        data = src.read_bytes()
        truncated = data[:real_end]
        if not truncated.endswith(b"\x00\x00\x01\xB9"):
            truncated += b"\x00\x00\x01\xB9"
        dst.write_bytes(truncated)
        saved = src.stat().st_size - real_end
        fixes = [f"truncated_garbage_{saved // (1024*1024)}_MB"]
        log.info(f"{src.name}: removed {saved // (1024*1024)} MB of trailing garbage")
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}

    if not issues:
        import shutil
        shutil.copy2(src, dst)
        return {"issues": [], "fixes": [], "success": True,
                "output_size": dst.stat().st_size}

    log.info(f"{src.name}: problems → {issues}")
    try:
        fixes = repair(src, dst)
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}
    except CorruptionError as e:
        return {"issues": issues, "fixes": [], "success": False,
                "error": str(e), "output_size": 0}
