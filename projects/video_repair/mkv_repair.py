# Author: Jordi Y Blanch
"""
Repairer for MKV / WebM files (EBML format).

Fixes:
  1. Unknown or wrong Segment size → marked as unknown (safe for players)
  2. Missing or corrupted SeekHead → rebuilt with the real element positions
  3. The old SeekHead, if any, is replaced with a Void element of the same size

Missing Cues are reported by diagnose() but not rebuilt.
"""
import struct
import logging
from pathlib import Path

from utils import CorruptionError, human_size

log = logging.getLogger(__name__)

# ── EBML IDs of the most important elements ───────────────────────────────────
EBML_HEADER   = 0x1A45DFA3
SEGMENT       = 0x18538067
SEEK_HEAD     = 0x114D9B74
SEEK          = 0x4DBB
SEEK_ID       = 0x53AB
SEEK_POSITION = 0x53AC
INFO          = 0x1549A966
TRACKS        = 0x1654AE6B
CLUSTER       = 0x1F43B675
CUES          = 0x1C53BB6B
CUE_POINT     = 0xBB
CUE_TIME      = 0xB3
CUE_TRACK_POS = 0xB7
CUE_TRACK     = 0xF7
CUE_CLUSTER   = 0xF1
TIMECODE      = 0xE7       # timecode inside a Cluster
VOID          = 0xEC
TAGS          = 0x1254C367
ATTACHMENTS   = 0x1941A469
CHAPTERS      = 0x1043A770

UNKNOWN_SIZE  = b"\x01\xFF\xFF\xFF\xFF\xFF\xFF\xFF"  # EBML unknown size


# ── EBML: reading variable-length integers ────────────────────────────────────
def _read_vint(data: bytes, pos: int) -> tuple[int, int]:
    """
    Read a VINT (variable-length integer) starting at `pos`.
    Returns (value, bytes_consumed).
    """
    if pos >= len(data):
        return -1, 0
    first = data[pos]
    if first == 0:
        return -1, 0

    width = 0
    mask = 0x80
    while mask > 0 and not (first & mask):
        width += 1
        mask >>= 1

    width += 1
    if pos + width > len(data):
        return -1, 0

    raw = int.from_bytes(data[pos:pos+width], "big")
    # Clear the width marker bit (it sits at bit 7 * width)
    raw &= (1 << (7 * width)) - 1
    return raw, width


def _read_element_id(data: bytes, pos: int) -> tuple[int, int]:
    """Read an EBML Element ID (same format as a VINT, but the width bit is kept)."""
    if pos >= len(data):
        return -1, 0
    first = data[pos]
    if first == 0:
        return -1, 0

    width = 0
    mask = 0x80
    while mask > 0 and not (first & mask):
        width += 1
        mask >>= 1
    width += 1

    if pos + width > len(data):
        return -1, 0

    element_id = int.from_bytes(data[pos:pos+width], "big")
    return element_id, width


def _encode_vint(value: int, min_width: int = 1) -> bytes:
    """Encode a value as an EBML VINT."""
    for width in range(1, 9):
        max_val = (1 << (7 * width)) - 2
        if value <= max_val and width >= min_width:
            raw = value | (1 << (7 * width))
            return raw.to_bytes(width, "big")
    raise ValueError(f"Value too large for a VINT: {value}")


def _encode_element_id(eid: int) -> bytes:
    """Encode an EBML Element ID as bytes."""
    if eid <= 0xFF:
        return eid.to_bytes(1, "big")
    elif eid <= 0xFFFF:
        return eid.to_bytes(2, "big")
    elif eid <= 0xFFFFFF:
        return eid.to_bytes(3, "big")
    else:
        return eid.to_bytes(4, "big")


def _make_element(eid: int, payload: bytes) -> bytes:
    """Build an EBML element with ID + size + payload."""
    return _encode_element_id(eid) + _encode_vint(len(payload)) + payload


def _void_element(total_size: int) -> bytes:
    """Build a Void element that takes up exactly `total_size` bytes."""
    for width in range(1, 9):
        payload_len = total_size - 1 - width
        if payload_len < 0:
            break
        size_bytes = _encode_vint(payload_len, min_width=width)
        if len(size_bytes) == width:
            return bytes([VOID]) + size_bytes + b"\x00" * payload_len
    raise ValueError(f"Cannot build a Void element of {total_size} bytes")


# ── Element scanning ──────────────────────────────────────────────────────────
class Element:
    __slots__ = ("eid", "pos", "header_size", "data_size", "unknown_size")

    def __init__(self, eid, pos, header_size, data_size, unknown_size=False):
        self.eid          = eid
        self.pos          = pos
        self.header_size  = header_size
        self.data_size    = data_size
        self.unknown_size = unknown_size

    @property
    def total_size(self):
        return self.header_size + (0 if self.unknown_size else self.data_size)

    @property
    def data_start(self):
        return self.pos + self.header_size


def _parse_element(data: bytes, pos: int) -> Element | None:
    start = pos
    eid, id_width = _read_element_id(data, pos)
    if eid < 0 or id_width == 0:
        return None
    pos += id_width

    size, sz_width = _read_vint(data, pos)
    if sz_width == 0:
        return None
    pos += sz_width

    unknown = (size == (1 << (7 * sz_width)) - 1)
    if unknown:
        size = len(data) - pos

    header_size = pos - start
    return Element(eid, start, header_size, size, unknown)


def _scan_top_level(data: bytes, seg_start: int) -> list[Element]:
    """Scan the top-level elements inside the Segment."""
    elements = []
    pos = seg_start

    while pos < len(data) - 4:
        el = _parse_element(data, pos)
        if el is None:
            pos += 1
            continue
        elements.append(el)
        if el.eid in (CLUSTER, INFO, TRACKS, CUES, SEEK_HEAD, TAGS,
                      ATTACHMENTS, CHAPTERS, VOID):
            if not el.unknown_size:
                pos += el.header_size + el.data_size
            else:
                pos += el.header_size + 1
        else:
            pos += max(el.header_size, 1)

    return elements


def _find_clusters(data: bytes, seg_start: int) -> list[tuple[int, int]]:
    """
    Find Clusters by scanning for their ID (0x1F43B675).
    Returns a list of (absolute_position, timecode).
    """
    clusters = []
    search = _encode_element_id(CLUSTER)
    pos = seg_start

    while pos < len(data) - 8:
        idx = data.find(search, pos)
        if idx == -1:
            break

        el = _parse_element(data, idx)
        if el is None or el.eid != CLUSTER:
            pos = idx + 1
            continue

        # Read the cluster's timecode (its first child element)
        inner = el.data_start
        tc    = 0
        while inner < el.data_start + min(64, el.data_size):
            tel = _parse_element(data, inner)
            if tel is None:
                break
            if tel.eid == TIMECODE:
                tc_bytes = data[tel.data_start: tel.data_start + tel.data_size]
                tc = int.from_bytes(tc_bytes, "big")
                break
            inner += tel.header_size + tel.data_size

        clusters.append((idx, tc))
        pos = idx + el.header_size + 1

    return clusters


# ── SeekHead construction ─────────────────────────────────────────────────────
def _build_seek_entry(eid: int, position: int) -> bytes:
    """A Seek element (points to an element by ID and position)."""
    id_bytes  = _encode_element_id(eid)
    seek_id   = _make_element(SEEK_ID, id_bytes)
    seek_pos  = _make_element(SEEK_POSITION, position.to_bytes(
        max(1, (position.bit_length() + 7) // 8), "big"))
    return _make_element(SEEK, seek_id + seek_pos)


def _build_seek_head(positions: dict[int, int]) -> bytes:
    """Build a complete SeekHead for the given elements."""
    seeks = b"".join(_build_seek_entry(eid, pos) for eid, pos in positions.items())
    return _make_element(SEEK_HEAD, seeks)


# ── Diagnosis ─────────────────────────────────────────────────────────────────
def diagnose(path: Path) -> dict:
    data   = path.read_bytes()
    issues = []

    if len(data) < 4:
        return {"issues": ["too_small"], "file_size": len(data)}

    el = _parse_element(data, 0)
    if el is None or el.eid != EBML_HEADER:
        issues.append("not_ebml")
        return {"issues": issues, "file_size": len(data)}

    seg_el = _parse_element(data, el.header_size + el.data_size)
    if seg_el is None or seg_el.eid != SEGMENT:
        issues.append("segment_missing")
        return {"issues": issues, "file_size": len(data)}

    if seg_el.unknown_size:
        issues.append("segment_size_unknown")

    seg_start = seg_el.data_start
    top_els   = {el.eid for el in _scan_top_level(data, seg_start)}

    if SEEK_HEAD not in top_els:
        issues.append("seekhead_missing")
    if CUES not in top_els:
        issues.append("cues_missing")
    if INFO not in top_els:
        issues.append("info_missing")

    return {"issues": issues, "file_size": len(data)}


# ── Repair ────────────────────────────────────────────────────────────────────
def repair(src: Path, dst: Path) -> list[str]:
    data  = src.read_bytes()
    fixes: list[str] = []

    # Locate the EBML header and the Segment
    ebml_el = _parse_element(data, 0)
    if ebml_el is None or ebml_el.eid != EBML_HEADER:
        raise CorruptionError("The EBML header was not found.")

    seg_offset = ebml_el.header_size + ebml_el.data_size
    seg_el     = _parse_element(data, seg_offset)
    if seg_el is None or seg_el.eid != SEGMENT:
        raise CorruptionError("The Segment element was not found.")

    seg_start = seg_el.data_start   # where the segment's elements begin

    # ── 1. Mark the Segment size as unknown (safest option) ──────────────────
    seg_id_bytes = _encode_element_id(SEGMENT)
    new_seg_header = seg_id_bytes + UNKNOWN_SIZE
    header_part = data[:seg_offset] + new_seg_header
    body_part   = data[seg_start:]
    data = header_part + body_part
    seg_start = len(header_part)
    fixes.append("segment_size_set_unknown")

    # ── 2. Scan the real clusters ─────────────────────────────────────────────
    clusters = _find_clusters(data, seg_start)
    log.info(f"Found {len(clusters)} clusters.")

    # ── 3. Find the positions of Info, Tracks and the rest ───────────────────
    top_elements = _scan_top_level(data, seg_start)
    positions: dict[int, int] = {}

    for el in top_elements:
        if el.eid in (INFO, TRACKS, CUES, TAGS, ATTACHMENTS, CHAPTERS):
            positions[el.eid] = el.pos - seg_start

    if clusters:
        positions[CLUSTER] = clusters[0][0] - seg_start

    # ── 4. Replace the old SeekHead, if any, with a Void of the same size ────
    old_sh = next((el for el in top_elements if el.eid == SEEK_HEAD), None)
    if old_sh:
        end = old_sh.pos + old_sh.total_size
        data = data[:old_sh.pos] + _void_element(old_sh.total_size) + data[end:]
        fixes.append("seekhead_old_voided")

    # ── 5. Build the new SeekHead ─────────────────────────────────────────────
    # It goes at the start of the Segment, so every position shifts by its own
    # length. Repeat until the length stops changing.
    shift = 0
    while True:
        new_seek_head = _build_seek_head({eid: p + shift for eid, p in positions.items()})
        if len(new_seek_head) == shift:
            break
        shift = len(new_seek_head)

    # Insert the new SeekHead at the start of the Segment
    data = data[:seg_start] + new_seek_head + data[seg_start:]
    fixes.append(f"seekhead_rebuilt_{len(positions)}_entries")

    dst.write_bytes(data)
    return fixes


def repair_mkv(src: Path, dst: Path) -> dict:
    info   = diagnose(src)
    issues = info["issues"]

    if not issues or issues == ["segment_size_unknown"]:
        import shutil
        shutil.copy2(src, dst)
        return {"issues": issues, "fixes": [], "success": True,
                "output_size": dst.stat().st_size}

    log.info(f"{src.name}: problems → {issues}")
    try:
        fixes = repair(src, dst)
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}
    except CorruptionError as e:
        return {"issues": issues, "fixes": [], "success": False, "error": str(e),
                "output_size": 0}
