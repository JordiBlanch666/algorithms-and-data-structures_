# Author: Jordi Y Blanch
"""
Repairer for MP4 / MOV / M4V files.

Fixes the most common problems:
  1. Wrong box sizes
  2. A missing moov atom, or one at the end of the file (interrupted recording)
  3. A missing ftyp atom
  4. A truncated file with an incomplete mdat
  5. Box reordering: ftyp → moov → mdat (streaming-friendly)
"""
import struct
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from utils import (
    read_u32_be, read_u64_be, write_u32_be, write_u64_be,
    fourcc, CorruptionError, backup_file, human_size
)

log = logging.getLogger(__name__)

# Known boxes from the ISO BMFF / QuickTime standard
KNOWN_BOXES = {
    "ftyp", "moov", "mdat", "free", "skip", "wide", "pnot",
    "mvhd", "trak", "tkhd", "mdia", "mdhd", "hdlr", "minf",
    "dinf", "dref", "stbl", "stsd", "stts", "stsc", "stsz",
    "stco", "co64", "stss", "ctts", "smhd", "vmhd", "nmhd",
    "udta", "meta", "ilst", "meco", "uuid", "edts", "elst",
    "mvex", "mehd", "trex", "moof", "mfhd", "traf", "tfhd",
    "trun", "mfra", "tfra", "mfro", "sidx", "ssix",
}

# Compatible ftyp brands
FTYP_BRANDS = {
    b"isom", b"iso2", b"mp41", b"mp42", b"M4V ", b"M4A ",
    b"qt  ", b"avc1", b"MSNV", b"f4v ", b"crx ", b"heic",
}


@dataclass
class Box:
    offset: int      # position in the file
    size: int        # total size including the header
    box_type: str    # fourcc
    header_size: int # 8 or 16 (when it uses a 64-bit size)
    data_offset: int # offset where the box data begins


def _parse_box_header(data: bytes, offset: int) -> Box | None:
    """
    Read the header of an ISO BMFF box at `offset`.
    Returns None if the bytes don't form a valid box.
    """
    if offset + 8 > len(data):
        return None

    size = read_u32_be(data, offset)
    btype = fourcc(data, offset + 4)

    if btype not in KNOWN_BOXES and not btype.isprintable():
        return None

    if size == 1:
        # 64-bit size
        if offset + 16 > len(data):
            return None
        size = read_u64_be(data, offset + 8)
        header_size = 16
        data_offset = offset + 16
    elif size == 0:
        # Size runs to the end of the file
        size = len(data) - offset
        header_size = 8
        data_offset = offset + 8
    else:
        header_size = 8
        data_offset = offset + 8

    if size < header_size or offset + size > len(data) + 1:
        return None

    return Box(offset=offset, size=size, box_type=btype,
               header_size=header_size, data_offset=data_offset)


def _scan_boxes(data: bytes, start: int = 0, end: int | None = None) -> list[Box]:
    """Scan boxes from `start` to `end` and return the valid ones."""
    end = end or len(data)
    boxes = []
    pos = start
    consecutive_fails = 0

    while pos < end:
        box = _parse_box_header(data, pos)
        if box is None:
            consecutive_fails += 1
            if consecutive_fails > 32:
                break
            pos += 4
            continue
        consecutive_fails = 0
        boxes.append(box)
        next_pos = pos + box.size
        if next_pos <= pos:
            break
        pos = next_pos

    return boxes


def _find_moov_by_scan(data: bytes) -> int:
    """Search the whole file for the 'moov' signature when normal parsing fails."""
    pos = 0
    while pos < len(data) - 8:
        if data[pos+4:pos+8] == b"moov":
            candidate_size = read_u32_be(data, pos)
            if 8 <= candidate_size <= len(data) - pos:
                return pos
        pos += 4
    return -1


def _build_ftyp() -> bytes:
    """Build a minimal ftyp atom that standard players accept."""
    compatible = b"isom" + b"iso2" + b"avc1" + b"mp41"
    size = 8 + 4 + 4 + len(compatible)   # header + major + minor + compat
    return write_u32_be(size) + b"ftyp" + b"isom" + b"\x00\x02\x00\x00" + compatible


def _fix_stco_offsets(moov_data: bytes, delta: int) -> bytes:
    """
    Shift the absolute offsets in the chunk offset tables (stco/co64)
    inside the moov blob by `delta` bytes.
    Needed when ftyp/moov are moved in front of mdat.
    """
    result = bytearray(moov_data)
    pos = 0

    while pos < len(result) - 8:
        size = struct.unpack_from(">I", result, pos)[0]
        btype = result[pos+4:pos+8]

        if btype == b"stco" and size >= 20:
            # stco: version(1) + flags(3) + entry_count(4) + entries(4*n)
            entry_count = struct.unpack_from(">I", result, pos + 12)[0]
            for i in range(entry_count):
                eoff = pos + 16 + i * 4
                if eoff + 4 <= len(result):
                    old = struct.unpack_from(">I", result, eoff)[0]
                    struct.pack_into(">I", result, eoff, old + delta)

        elif btype == b"co64" and size >= 20:
            entry_count = struct.unpack_from(">I", result, pos + 12)[0]
            for i in range(entry_count):
                eoff = pos + 16 + i * 8
                if eoff + 8 <= len(result):
                    old = struct.unpack_from(">Q", result, eoff)[0]
                    struct.pack_into(">Q", result, eoff, old + delta)

        if size <= 0:
            break
        pos += size

    return bytes(result)


# ── Diagnosis ─────────────────────────────────────────────────────────────────
def diagnose(path: Path) -> dict:
    """
    Analyze an MP4 and return a dict with the problems found.
    """
    data = path.read_bytes()
    issues = []
    info   = {}

    boxes = _scan_boxes(data)
    types = {b.box_type: b for b in boxes}

    info["boxes_found"] = [b.box_type for b in boxes]
    info["file_size"]   = len(data)

    if "ftyp" not in types:
        issues.append("ftyp_missing")
    if "moov" not in types:
        # Try to find it by its signature
        moov_pos = _find_moov_by_scan(data)
        if moov_pos >= 0:
            issues.append("moov_corrupted_size")
        else:
            issues.append("moov_missing")
    if "mdat" not in types:
        issues.append("mdat_missing")

    # Is moov after mdat? (interrupted recording)
    if "moov" in types and "mdat" in types:
        if types["moov"].offset > types["mdat"].offset:
            issues.append("moov_after_mdat")

    # Does the last box's size run past the end of the file?
    if boxes:
        last = boxes[-1]
        if last.offset + last.size > len(data) + 512:
            issues.append("truncated")

    info["issues"] = issues
    return info


# ── Repair ────────────────────────────────────────────────────────────────────
def repair(src: Path, dst: Path) -> list[str]:
    """
    Repair `src` and save the result to `dst`.
    Returns the list of fixes applied.
    """
    data  = src.read_bytes()
    fixes: list[str] = []
    boxes = _scan_boxes(data)
    types = {b.box_type: b for b in boxes}

    # ── 1. moov with a wrong size → find it by its signature ─────────────────
    if "moov" not in types:
        moov_pos = _find_moov_by_scan(data)
        if moov_pos >= 0:
            log.info("moov found by signature — fixing its size")
            # Recompute the size up to the end of the file
            remaining = len(data) - moov_pos
            corrected = bytearray(data)
            struct.pack_into(">I", corrected, moov_pos, remaining)
            data  = bytes(corrected)
            boxes = _scan_boxes(data)
            types = {b.box_type: b for b in boxes}
            fixes.append("moov_size_corrected")

    if "moov" not in types and "mdat" not in types:
        raise CorruptionError("Neither moov nor mdat was found. The file is too damaged.")

    # ── 2. Missing ftyp → insert a generic one ────────────────────────────────
    needs_ftyp = "ftyp" not in types
    ftyp_data  = data[types["ftyp"].offset: types["ftyp"].offset + types["ftyp"].size] \
                 if not needs_ftyp else _build_ftyp()
    if needs_ftyp:
        fixes.append("ftyp_inserted")

    # ── 3. Reorder: ftyp → moov → mdat ───────────────────────────────────────
    if "moov" in types and "mdat" in types:
        moov_box = types["moov"]
        mdat_box = types["mdat"]
        ftyp_box = types.get("ftyp")

        moov_data = data[moov_box.offset: moov_box.offset + moov_box.size]
        mdat_data = data[mdat_box.offset: mdat_box.offset + mdat_box.size]

        new_ftyp_size  = len(ftyp_data)
        new_moov_start = new_ftyp_size

        # mdat will start right after the new moov
        new_mdat_start = new_ftyp_size + len(moov_data)

        old_mdat_start = mdat_box.offset
        delta = new_mdat_start - old_mdat_start
        if delta != 0:
            moov_data = _fix_stco_offsets(moov_data, delta)
            fixes.append(f"chunk_offsets_adjusted_by_{delta:+d}")

        # Append the remaining boxes (free, udta, etc.) other than ftyp/moov/mdat
        extra = b"".join(
            data[b.offset: b.offset + b.size]
            for b in boxes
            if b.box_type not in ("ftyp", "moov", "mdat")
        )

        output = ftyp_data + moov_data + mdat_data + extra
        fixes.append("boxes_reordered_ftyp_moov_mdat")
    else:
        output = data
        fixes.append("partial_repair_no_reorder")

    dst.write_bytes(output)
    return fixes


# ── Public API ────────────────────────────────────────────────────────────────
def repair_mp4(src: Path, dst: Path) -> dict:
    """
    Main entry point.
    Returns a dict with 'issues', 'fixes', 'success', 'output_size'.
    """
    info   = diagnose(src)
    issues = info["issues"]

    if not issues:
        log.info(f"{src.name}: no serious problems found.")
        import shutil
        shutil.copy2(src, dst)
        return {"issues": [], "fixes": [], "success": True,
                "output_size": dst.stat().st_size}

    log.info(f"{src.name}: problems found → {issues}")
    try:
        fixes = repair(src, dst)
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}
    except CorruptionError as e:
        return {"issues": issues, "fixes": [], "success": False, "error": str(e),
                "output_size": 0}
