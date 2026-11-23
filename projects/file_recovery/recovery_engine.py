# Author: Jordi Y Blanch
"""
Main recovery engine.
Coordinates MFTParser + FileCarver, removes duplicates and saves the files.
"""
import hashlib
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from disk_reader import DiskReader
from file_carver import CarvedFile, FileCarver
from mft_parser import MFTEntry, MFTParser

log = logging.getLogger(__name__)


@dataclass
class RecoveryStats:
    scanned_bytes: int = 0
    mft_found: int     = 0
    carved_found: int  = 0
    saved: int         = 0
    skipped: int       = 0
    errors: int        = 0


@dataclass
class RecoveryOptions:
    disk_path: str               # ej. r'\\.\\C:'
    output_dir: Path
    images: bool         = True
    videos: bool         = True
    use_mft: bool        = True  # method 1: parse the NTFS MFT
    use_carving: bool    = True  # method 2: sector-level file carving
    min_size: int        = 10_000        # 10 KB minimum
    max_size: int        = 100 * 1024**3 # 100 GB maximum
    deduplicate: bool    = True          # don't save two identical files
    overwrite: bool      = False
    hint_paths: list[str] | None = None  # paths that narrow down the carving area
    progress_cb: Callable[[str, int, int], None] | None = None


class RecoveryEngine:
    """
    Orchestrates the recovery of deleted images and videos.

    Example:
        opts = RecoveryOptions(
            disk_path=r'\\.\\C:',
            output_dir=Path('C:/Recovered'),
        )
        engine = RecoveryEngine(opts)
        stats  = engine.run()
        print(stats)
    """

    def __init__(self, opts: RecoveryOptions):
        self.opts   = opts
        self.stats  = RecoveryStats()
        self._seen_hashes: set[str] = set()

    # ── Entry point ──────────────────────────────────────────────────────────
    def run(self) -> RecoveryStats:
        opts = self.opts
        opts.output_dir.mkdir(parents=True, exist_ok=True)

        log.info(f"Opening disk: {opts.disk_path}")
        with DiskReader(opts.disk_path) as reader:
            info = reader.info()
            log.info(f"Disk: {info}")
            self.stats.scanned_bytes = info.total_bytes

            if opts.use_mft:
                self._run_mft(reader)
            if opts.use_carving:
                self._run_carving(reader)

        log.info(
            f"Recovery finished — "
            f"MFT: {self.stats.mft_found}, "
            f"Carving: {self.stats.carved_found}, "
            f"Saved: {self.stats.saved}, "
            f"Skipped: {self.stats.skipped}"
        )
        return self.stats

    # ── Method 1: MFT ─────────────────────────────────────────────────────────
    def _run_mft(self, reader: DiskReader):
        log.info("── Starting MFT analysis ──")
        parser = MFTParser(reader, cluster_size=4096, sector_size=reader.sector_size)

        for entry in parser.find_deleted():
            self.stats.mft_found += 1
            self._notify(f"[MFT] {entry.filename}", self.stats.mft_found, 0)

            if not self._size_ok(entry.size):
                self.stats.skipped += 1
                continue

            try:
                data = parser.read_file_data(entry)
                self._save_from_mft(entry, data)
            except Exception as e:
                log.warning(f"Error recovering '{entry.filename}': {e}")
                self.stats.errors += 1

    def _save_from_mft(self, entry: MFTEntry, data: bytes):
        if not data:
            self.stats.skipped += 1
            return
        if self._is_duplicate(data):
            self.stats.skipped += 1
            return

        category = _category_for_ext(entry.extension)
        dest_dir = self.opts.output_dir / "mft" / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest = dest_dir / _safe_name(entry.filename)
        dest = _unique_path(dest, self.opts.overwrite)
        dest.write_bytes(data)
        self.stats.saved += 1
        log.info(f"  Saved (MFT): {dest}")

    # ── Method 2: File carving ────────────────────────────────────────────────
    def _run_carving(self, reader: DiskReader):
        log.info("── Starting file carving ──")

        scan_ranges: list[tuple[int, int]] = []
        if self.opts.hint_paths:
            from cluster_locator import get_scan_ranges
            volume = self.opts.disk_path.replace("\\\\.\\", "")
            log.info(f"Locating clusters for {len(self.opts.hint_paths)} paths...")
            scan_ranges = get_scan_ranges(
                self.opts.hint_paths, volume,
                sector_size=reader.sector_size,
            )
            if scan_ranges:
                total_gb = sum(e - s for s, e in scan_ranges) * reader.sector_size / 1024**3
                log.info(f"Scan narrowed to {total_gb:.2f} GB in {len(scan_ranges)} area(s)")
            else:
                log.warning("Could not locate the clusters — running a full scan")

        if scan_ranges:
            # Scan only the ranges that were found
            for start_sector, end_sector in scan_ranges:
                carver = FileCarver(
                    reader,
                    images       = self.opts.images,
                    videos       = self.opts.videos,
                    start_sector = start_sector,
                    end_sector   = min(end_sector, reader.total_sectors),
                )
                for carved in carver.scan():
                    self._process_carved(carved, reader)
        else:
            carver = FileCarver(reader, images=self.opts.images, videos=self.opts.videos)
            for carved in carver.scan():
                self._process_carved(carved, reader)

    def _process_carved(self, carved, reader):
        self.stats.carved_found += 1
        self._notify(
            f"[Carving] {carved.signature.description} "
            f"@ {carved.start_byte // (1024**2):.1f} MB",
            self.stats.carved_found,
            reader.total_bytes,
        )
        if not self._size_ok(carved.estimated_size):
            self.stats.skipped += 1
            return
        if self._is_duplicate(carved.probe):
            self.stats.skipped += 1
            return
        self._save_carved(carved)

    def _save_carved(self, carved: CarvedFile):
        category = carved.signature.category
        dest_dir = self.opts.output_dir / "carving" / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest = dest_dir / carved.suggested_name
        dest = _unique_path(dest, self.opts.overwrite)
        written = carved.write_to(dest)
        if written == 0:
            dest.unlink(missing_ok=True)
            self.stats.skipped += 1
            return
        self.stats.saved += 1
        log.info(f"  Saved (carving): {dest} ({written // 1024} KB)")

    # ── Internal helpers ──────────────────────────────────────────────────────
    def _size_ok(self, size: int) -> bool:
        return self.opts.min_size <= size <= self.opts.max_size

    def _is_duplicate(self, data: bytes) -> bool:
        if not self.opts.deduplicate or not data:
            return False
        h = hashlib.md5(data, usedforsecurity=False).hexdigest()
        if h in self._seen_hashes:
            return True
        self._seen_hashes.add(h)
        return False

    def _notify(self, msg: str, current: int, total: int):
        if self.opts.progress_cb:
            self.opts.progress_cb(msg, current, total)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _category_for_ext(ext: str) -> str:
    images = {"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff",
               "webp", "heic", "heif", "cr2", "cr3", "nef", "arw",
               "dng", "orf", "rw2"}
    return "images" if ext in images else "videos"


def _safe_name(name: str) -> str:
    forbidden = r'\/:*?"<>|'
    return "".join("_" if c in forbidden else c for c in name)


def _unique_path(path: Path, overwrite: bool) -> Path:
    if overwrite or not path.exists():
        return path
    stem   = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1
