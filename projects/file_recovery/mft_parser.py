# Author: Jordi Y Blanch
"""
Parser for the NTFS Master File Table (MFT).
Finds entries of deleted files ("in use" flag = 0) with image and
video extensions so they can be recovered.

MFT format:
  - Each entry takes 1024 bytes (by default)
  - It starts with the signature b"FILE"
  - The Flags field says whether the file is active or deleted
"""
import struct
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from disk_reader import DiskReader

log = logging.getLogger(__name__)


# ── NTFS constants ────────────────────────────────────────────────────────────
MFT_SIGNATURE          = b"FILE"
MFT_RECORD_SIZE        = 1024    # bytes per MFT entry
MFT_FLAG_IN_USE        = 0x0001  # file in use
MFT_FLAG_DIRECTORY     = 0x0002

# Relevant NTFS attribute types
ATTR_STANDARD_INFORMATION = 0x10
ATTR_FILE_NAME            = 0x30
ATTR_DATA                 = 0x80
ATTR_END                  = 0xFFFFFFFF

# Target extensions
TARGET_EXTENSIONS = {
    # images
    "jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff",
    "webp", "heic", "heif",
    # RAW
    "cr2", "cr3", "nef", "arw", "dng", "orf", "rw2",
    # video
    "mp4", "m4v", "mov", "avi", "mkv", "wmv", "flv",
    "mpg", "mpeg", "3gp", "mts", "m2ts", "vob",
}


# ── Data structures ──────────────────────────────────────────────────────────
@dataclass
class MFTEntry:
    mft_index: int
    filename: str
    extension: str
    size: int          # logical bytes of the $DATA attribute
    is_deleted: bool
    data_runs: list[tuple[int, int]]  # (cluster_offset, cluster_count)


# ── MFT decoding functions ─────────────────────────────────────────────────
def _apply_fixup(raw: bytes) -> bytes:
    """Apply the Update Sequence Array (USA) to fix MFT sectors."""
    if len(raw) < 48:
        return raw
    usa_offset = struct.unpack_from("<H", raw, 4)[0]
    usa_count  = struct.unpack_from("<H", raw, 6)[0]
    if usa_offset + usa_count * 2 > len(raw):
        return raw
    data = bytearray(raw)
    for i in range(1, usa_count):
        sector_end = i * 512 - 2
        if sector_end + 2 > len(data):
            break
        data[sector_end]     = raw[usa_offset + i * 2]
        data[sector_end + 1] = raw[usa_offset + i * 2 + 1]
    return bytes(data)


def _parse_filename_attr(attr_data: bytes) -> tuple[str, int]:
    """
    Return (file_name, logical_size) from a $FILE_NAME attribute.
    Offset 64 = allocated logical size, offset 80 = name length.
    """
    if len(attr_data) < 66:
        return "", 0
    allocated_size = struct.unpack_from("<Q", attr_data, 48)[0]
    real_size      = struct.unpack_from("<Q", attr_data, 56)[0]
    name_len       = attr_data[64]
    name_start     = 66
    name_end       = name_start + name_len * 2
    if name_end > len(attr_data):
        return "", real_size
    try:
        name = attr_data[name_start:name_end].decode("utf-16-le")
    except UnicodeDecodeError:
        name = ""
    return name, real_size


def _parse_data_runs(run_bytes: bytes, cluster_size: int) -> list[tuple[int, int]]:
    """
    Decode NTFS data runs. Returns a list of (start_cluster, num_clusters).
    start_cluster = -1 means non-resident data with no position (sparse).
    """
    runs = []
    pos  = 0
    vcn  = 0
    while pos < len(run_bytes):
        header = run_bytes[pos]
        if header == 0:
            break
        len_bytes = header & 0x0F   # low nibble: length bytes
        off_bytes = header >> 4     # high nibble: offset bytes
        pos += 1

        if pos + len_bytes + off_bytes > len(run_bytes):
            break

        run_len = int.from_bytes(run_bytes[pos: pos + len_bytes], "little")
        pos += len_bytes

        if off_bytes == 0:
            vcn += run_len
            continue

        run_offset_raw = run_bytes[pos: pos + off_bytes]
        pos += off_bytes
        # The offset is signed (relative to the previous run)
        run_offset = int.from_bytes(run_offset_raw, "little", signed=False)
        if run_offset_raw and (run_offset_raw[-1] & 0x80):
            run_offset -= 1 << (off_bytes * 8)
        vcn += run_offset

        runs.append((vcn, run_len))

    return runs


def _parse_mft_record(raw: bytes, mft_index: int) -> MFTEntry | None:
    """Try to parse an MFT entry; returns an MFTEntry, or None if it isn't valid."""
    if len(raw) < MFT_RECORD_SIZE or raw[:4] != MFT_SIGNATURE:
        return None

    raw = _apply_fixup(raw)

    flags = struct.unpack_from("<H", raw, 22)[0]
    is_deleted = not bool(flags & MFT_FLAG_IN_USE)

    attr_offset = struct.unpack_from("<H", raw, 20)[0]
    pos = attr_offset

    filename  = ""
    file_size = 0
    data_runs: list[tuple[int, int]] = []

    while pos + 8 <= MFT_RECORD_SIZE:
        attr_type   = struct.unpack_from("<I", raw, pos)[0]
        if attr_type == ATTR_END:
            break
        attr_len    = struct.unpack_from("<I", raw, pos + 4)[0]
        if attr_len == 0 or pos + attr_len > MFT_RECORD_SIZE:
            break

        non_resident = raw[pos + 8]
        attr_body_off = struct.unpack_from("<H", raw, pos + 20)[0]
        attr_body = raw[pos + attr_body_off: pos + attr_len]

        if attr_type == ATTR_FILE_NAME and not non_resident:
            name, size = _parse_filename_attr(attr_body)
            if name and "$" not in name:   # skip system metafiles
                filename  = name
                file_size = size

        elif attr_type == ATTR_DATA and non_resident:
            # Read the data runs from the non-resident attribute header
            run_offset = struct.unpack_from("<H", raw, pos + 32)[0]
            run_data   = raw[pos + run_offset: pos + attr_len]
            alloc_size = struct.unpack_from("<Q", raw, pos + 40)[0]
            real_size  = struct.unpack_from("<Q", raw, pos + 48)[0]
            if real_size:
                file_size = real_size
            data_runs = _parse_data_runs(run_data, cluster_size=4096)

        pos += attr_len

    if not filename:
        return None

    ext = Path(filename).suffix.lstrip(".").lower()
    if ext not in TARGET_EXTENSIONS:
        return None

    return MFTEntry(
        mft_index  = mft_index,
        filename   = filename,
        extension  = ext,
        size       = file_size,
        is_deleted = is_deleted,
        data_runs  = data_runs,
    )


# ── Main class ────────────────────────────────────────────────────────────────
class MFTParser:
    """
    Reads and parses the MFT of an NTFS volume to find deleted
    image/video files.

    Usage:
        parser = MFTParser(disk_reader, cluster_size=4096, sector_size=512)
        for entry in parser.find_deleted():
            print(entry.filename, entry.size)
    """

    def __init__(self, reader: DiskReader, cluster_size: int = 4096,
                 sector_size: int = 512):
        self.reader       = reader
        self.cluster_size = cluster_size
        self.sector_size  = sector_size

    def _find_mft_start(self) -> int:
        """
        Read the NTFS Boot Sector (sector 0) to get the $MFT offset.
        Returns the offset in bytes, or -1 if it isn't NTFS.
        """
        boot = self.reader.read_sectors(0, 1)
        if len(boot) < 512:
            return -1

        # NTFS OEM signature at offset 3
        if boot[3:11] != b"NTFS    ":
            log.warning("The volume doesn't look like NTFS (OEM signature not found).")
            return -1

        bytes_per_sector  = struct.unpack_from("<H", boot, 11)[0]
        sectors_per_clust = boot[13]
        mft_cluster       = struct.unpack_from("<Q", boot, 48)[0]

        self.sector_size  = bytes_per_sector or 512
        self.cluster_size = sectors_per_clust * self.sector_size

        mft_byte_offset = mft_cluster * self.cluster_size
        log.info(f"MFT found at offset {mft_byte_offset:#x} "
                 f"(cluster {mft_cluster})")
        return mft_byte_offset

    def find_deleted(self, include_active: bool = False) -> Iterator[MFTEntry]:
        """
        Iterate over every MFT entry and yield deleted files
        (or active ones if include_active=True) with image/video extensions.
        """
        mft_offset = self._find_mft_start()
        if mft_offset < 0:
            log.error("Could not locate the MFT. Is this an NTFS volume?")
            return

        index = 0
        offset = mft_offset

        while offset + MFT_RECORD_SIZE <= self.reader.total_bytes:
            try:
                raw = self.reader.read_bytes_at(offset, MFT_RECORD_SIZE)
            except OSError as e:
                log.debug(f"Error reading MFT[{index}]: {e}")
                offset += MFT_RECORD_SIZE
                index  += 1
                continue

            if raw[:4] != MFT_SIGNATURE:
                # End of the MFT or a corrupted area
                break

            entry = _parse_mft_record(raw, index)
            if entry and (entry.is_deleted or include_active):
                yield entry

            offset += MFT_RECORD_SIZE
            index  += 1

    def read_file_data(self, entry: MFTEntry) -> bytes:
        """
        Rebuild a file's contents from its data runs.
        Returns bytes (may be incomplete if there are damaged sectors).
        """
        chunks: list[bytes] = []
        total_read = 0

        for cluster_start, cluster_count in entry.data_runs:
            if total_read >= entry.size:
                break
            byte_offset = cluster_start * self.cluster_size
            byte_length = cluster_count * self.cluster_size
            remaining   = entry.size - total_read
            to_read     = min(byte_length, remaining)

            try:
                data = self.reader.read_bytes_at(byte_offset, to_read)
                chunks.append(data)
                total_read += len(data)
            except OSError as e:
                log.warning(f"Damaged sector while reading '{entry.filename}': {e}")
                chunks.append(b"\x00" * to_read)
                total_read += to_read

        return b"".join(chunks)[: entry.size]
