# Author: Jordi Y Blanch
"""
Database of file signatures (magic bytes) for images and videos.
Each signature defines how to detect, size and name the recovered file.
"""
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class FileSignature:
    extension: str
    category: str          # "image" | "video" | "raw"
    header: bytes          # required header bytes
    header_offset: int     # offset inside the sector where the signature appears
    footer: Optional[bytes]  # footer bytes (None = estimated size)
    max_size: int          # maximum expected size in bytes
    description: str
    extra_checks: dict[int, bytes] = field(default_factory=dict)
    validator: Optional[Callable[[bytes], bool]] = field(default=None, compare=False)


# ─────────────────────────────────────────────
# IMAGES
# ─────────────────────────────────────────────
IMAGE_SIGNATURES: list[FileSignature] = [
    FileSignature(
        extension="jpg",
        category="image",
        header=b"\xFF\xD8\xFF",
        header_offset=0,
        footer=b"\xFF\xD9",
        max_size=50 * 1024 * 1024,   # 50 MB
        description="JPEG / JFIF / EXIF",
    ),
    FileSignature(
        extension="png",
        category="image",
        header=b"\x89PNG\r\n\x1A\n",
        header_offset=0,
        footer=b"\x00\x00\x00\x00IEND\xAEB`\x82",
        max_size=100 * 1024 * 1024,  # 100 MB
        description="PNG",
    ),
    FileSignature(
        extension="gif",
        category="image",
        header=b"GIF8",
        header_offset=0,
        footer=b"\x00;",
        max_size=20 * 1024 * 1024,   # 20 MB
        description="GIF87a / GIF89a",
    ),
    FileSignature(
        extension="bmp",
        category="image",
        header=b"BM",
        header_offset=0,
        footer=None,
        max_size=200 * 1024 * 1024,  # 200 MB (uncompressed bitmaps)
        description="Windows Bitmap",
    ),
    FileSignature(
        extension="tif",
        category="image",
        header=b"II*\x00",           # little-endian TIFF
        header_offset=0,
        footer=None,
        max_size=500 * 1024 * 1024,
        description="TIFF (little-endian)",
    ),
    FileSignature(
        extension="tif",
        category="image",
        header=b"MM\x00*",           # big-endian TIFF
        header_offset=0,
        footer=None,
        max_size=500 * 1024 * 1024,
        description="TIFF (big-endian)",
    ),
    FileSignature(
        extension="webp",
        category="image",
        header=b"RIFF",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024,
        description="WebP",
        extra_checks={8: b"WEBP"},   # bytes 8-11 must be "WEBP"
    ),
    FileSignature(
        extension="heic",
        category="image",
        header=b"ftyp",
        header_offset=4,             # the first 4 bytes are a variable size
        footer=None,
        max_size=100 * 1024 * 1024,
        description="HEIC / HEIF",
        extra_checks={8: b"heic"},
    ),
    # ── Camera RAW formats ──────────────────────────────────────────────
    FileSignature(
        extension="cr2",
        category="raw",
        header=b"II*\x00\x10\x00\x00\x00CR",  # Canon RAW v2
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024,
        description="Canon RAW CR2",
    ),
    FileSignature(
        extension="cr3",
        category="raw",
        header=b"ftyp",
        header_offset=4,
        footer=None,
        max_size=100 * 1024 * 1024,
        description="Canon RAW CR3",
        extra_checks={8: b"crx "},
    ),
    FileSignature(
        extension="nef",
        category="raw",
        header=b"II*\x00",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024,
        description="Nikon NEF (TIFF-based)",
        # NEF differs from a generic TIFF by its maker-notes IFD;
        # the carver saves it as .tif when there's no extra marker
    ),
    FileSignature(
        extension="arw",
        category="raw",
        header=b"II*\x00\x08\x00\x00\x00",
        header_offset=0,
        footer=None,
        max_size=100 * 1024 * 1024,
        description="Sony ARW",
    ),
    FileSignature(
        extension="dng",
        category="raw",
        header=b"II*\x00",
        header_offset=0,
        footer=None,
        max_size=100 * 1024 * 1024,
        description="Adobe DNG",
    ),
    FileSignature(
        extension="orf",
        category="raw",
        header=b"IIRO",
        header_offset=0,
        footer=None,
        max_size=30 * 1024 * 1024,
        description="Olympus ORF",
    ),
    FileSignature(
        extension="rw2",
        category="raw",
        header=b"IIU\x00",
        header_offset=0,
        footer=None,
        max_size=30 * 1024 * 1024,
        description="Panasonic RW2",
    ),
]

# ─────────────────────────────────────────────
# VIDEOS
# ─────────────────────────────────────────────
VIDEO_SIGNATURES: list[FileSignature] = [
    FileSignature(
        extension="mp4",
        category="video",
        header=b"ftypisom",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,   # 50 GB
        description="MP4 (ISO Base Media)",
    ),
    FileSignature(
        extension="mp4",
        category="video",
        header=b"ftypmp42",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="MP4 v2",
    ),
    FileSignature(
        extension="mp4",
        category="video",
        header=b"ftypMSNV",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="MP4 Sony PSP",
    ),
    FileSignature(
        extension="m4v",
        category="video",
        header=b"ftypm4v ",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="iTunes Video M4V",
    ),
    FileSignature(
        extension="mov",
        category="video",
        header=b"ftypqt  ",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="QuickTime MOV",
    ),
    FileSignature(
        extension="mov",
        category="video",
        header=b"moov",
        header_offset=4,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="QuickTime MOV (moov atom)",
    ),
    FileSignature(
        extension="avi",
        category="video",
        header=b"RIFF",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="AVI",
        extra_checks={8: b"AVI "},
    ),
    FileSignature(
        extension="mkv",
        category="video",
        header=b"\x1A\x45\xDF\xA3",
        header_offset=0,
        footer=None,
        max_size=100 * 1024 * 1024 * 1024,  # 100 GB
        description="Matroska MKV / WebM",
    ),
    FileSignature(
        extension="wmv",
        category="video",
        header=b"\x30\x26\xB2\x75\x8E\x66\xCF\x11",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="Windows Media Video / ASF",
    ),
    FileSignature(
        extension="flv",
        category="video",
        header=b"FLV\x01",
        header_offset=0,
        footer=None,
        max_size=20 * 1024 * 1024 * 1024,
        description="Flash Video FLV",
    ),
    FileSignature(
        extension="mpg",
        category="video",
        header=b"\x00\x00\x01\xBA",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="MPEG-2 Program Stream",
    ),
    FileSignature(
        extension="mpg",
        category="video",
        header=b"\x00\x00\x01\xB3",
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="MPEG-1 Video",
    ),
    FileSignature(
        extension="3gp",
        category="video",
        header=b"ftyp3gp",
        header_offset=4,
        footer=None,
        max_size=5 * 1024 * 1024 * 1024,
        description="3GPP Mobile Video",
    ),
    FileSignature(
        extension="mts",
        category="video",
        header=b"\x47",             # MPEG-TS sync byte (188-byte packets)
        header_offset=0,
        footer=None,
        max_size=50 * 1024 * 1024 * 1024,
        description="AVCHD / BDAV MPEG-TS",
    ),
    FileSignature(
        extension="vob",
        category="video",
        header=b"\x00\x00\x01\xBA",
        header_offset=0,
        footer=None,
        max_size=1024 * 1024 * 1024,
        description="DVD Video Object VOB",
    ),
]

ALL_SIGNATURES: list[FileSignature] = IMAGE_SIGNATURES + VIDEO_SIGNATURES


def get_signatures(images: bool = True, videos: bool = True) -> list[FileSignature]:
    result = []
    if images:
        result.extend(IMAGE_SIGNATURES)
    if videos:
        result.extend(VIDEO_SIGNATURES)
    return result
