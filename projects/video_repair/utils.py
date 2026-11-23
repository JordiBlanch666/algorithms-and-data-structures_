# Author: Jordi Y Blanch
"""
Shared helpers for parsing and writing binary video structures.
"""
import struct
from pathlib import Path


def read_u8(data: bytes, offset: int) -> int:
    return data[offset]

def read_u16_be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]

def read_u32_be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]

def read_u64_be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">Q", data, offset)[0]

def read_u32_le(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]

def write_u32_be(value: int) -> bytes:
    return struct.pack(">I", value)

def write_u64_be(value: int) -> bytes:
    return struct.pack(">Q", value)

def write_u32_le(value: int) -> bytes:
    return struct.pack("<I", value)

def fourcc(data: bytes, offset: int) -> str:
    return data[offset:offset+4].decode("latin-1", errors="replace")


class CorruptionError(Exception):
    """Error found while analyzing a video file."""


def backup_file(path: Path) -> Path:
    """Create a .bak copy of the file before repairing it."""
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
    return bak


def file_size(path: Path) -> int:
    return path.stat().st_size


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
