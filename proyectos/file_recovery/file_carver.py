# Autor: Jordi Y Blanch
"""
File Carver: escanea sectores crudos buscando firmas (magic bytes) de
imágenes y vídeos, independientemente del sistema de ficheros.

Funciona incluso cuando la MFT está corrupta o el sistema de ficheros
está formateado, ya que trabaja directamente sobre los datos del disco.
"""
import logging
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from disk_reader import DiskReader
from signatures import FileSignature, get_signatures

log = logging.getLogger(__name__)

DEFAULT_CHUNK_SECTORS = 2048
STREAM_CHUNK = 4 * 1024 * 1024   # 4 MB por chunk al escribir a disco


@dataclass
class CarvedFile:
    signature: FileSignature
    start_byte: int
    estimated_size: int
    probe: bytes          # primer MB para validación (no se carga todo en RAM)
    reader: object        # DiskReader para streaming al guardar

    @property
    def suggested_name(self) -> str:
        mb = self.start_byte // (1024 * 1024)
        return f"carved_{mb:06d}MB.{self.signature.extension}"

    def write_to(self, dest_path: Path) -> int:
        """Escribe el archivo al disco en chunks de 4 MB. Devuelve bytes escritos."""
        written = 0
        remaining = self.estimated_size
        offset = self.start_byte
        with open(dest_path, "wb") as f:
            while remaining > 0:
                to_read = min(STREAM_CHUNK, remaining)
                try:
                    chunk = self.reader.read_bytes_at(offset, to_read)
                except OSError:
                    break
                f.write(chunk)
                written += len(chunk)
                offset += len(chunk)
                remaining -= len(chunk)
        return written


# ── Estimadores de tamaño por formato ────────────────────────────────────────
def _estimate_jpeg_size(data: bytes) -> int:
    end = data.find(b"\xFF\xD9")
    return (end + 2) if end != -1 else 0


def _estimate_png_size(data: bytes) -> int:
    footer = b"\x00\x00\x00\x00IEND\xAEB`\x82"
    end = data.find(footer)
    return (end + len(footer)) if end != -1 else 0


def _estimate_gif_size(data: bytes) -> int:
    end = data.find(b"\x00;")
    return (end + 2) if end != -1 else 0


def _estimate_bmp_size(data: bytes) -> int:
    if len(data) >= 6:
        return struct.unpack_from("<I", data, 2)[0]
    return 0


def _estimate_riff_size(data: bytes) -> int:
    if len(data) >= 8:
        return struct.unpack_from("<I", data, 4)[0] + 8
    return 0


def _estimate_mp4_size(data: bytes) -> int:
    pos   = 0
    total = 0
    limit = min(len(data), 64 * 1024 * 1024)
    while pos + 8 <= limit:
        box_size = struct.unpack_from(">I", data, pos)[0]
        if box_size == 0:
            break
        if box_size == 1:
            if pos + 16 > limit:
                break
            box_size = struct.unpack_from(">Q", data, pos + 8)[0]
        total += box_size
        pos   += box_size
    return total


def _estimate_mkv_size(data: bytes) -> int:
    return 0


def _estimate_avi_size(data: bytes) -> int:
    return _estimate_riff_size(data)


SIZE_ESTIMATORS = {
    "jpg":  _estimate_jpeg_size,
    "jpeg": _estimate_jpeg_size,
    "png":  _estimate_png_size,
    "gif":  _estimate_gif_size,
    "bmp":  _estimate_bmp_size,
    "webp": _estimate_riff_size,
    "avi":  _estimate_avi_size,
    "mp4":  _estimate_mp4_size,
    "m4v":  _estimate_mp4_size,
    "mov":  _estimate_mp4_size,
    "3gp":  _estimate_mp4_size,
    "mkv":  _estimate_mkv_size,
}


# ── Verificación de firmas ────────────────────────────────────────────────────
def _matches(sig: FileSignature, window: bytes, window_offset: int) -> bool:
    abs_hdr_start = sig.header_offset
    local = window_offset + abs_hdr_start

    if local + len(sig.header) > len(window):
        return False
    if window[local: local + len(sig.header)] != sig.header:
        return False

    for extra_off, extra_bytes in sig.extra_checks.items():
        check_pos = window_offset + extra_off
        if check_pos + len(extra_bytes) > len(window):
            return False
        if window[check_pos: check_pos + len(extra_bytes)] != extra_bytes:
            return False

    return True


# ── Clase principal ───────────────────────────────────────────────────────────
class FileCarver:
    def __init__(
        self,
        reader: DiskReader,
        images: bool = True,
        videos: bool = True,
        chunk_sectors: int = DEFAULT_CHUNK_SECTORS,
        start_sector: int = 0,
        end_sector: int | None = None,
    ):
        self.reader        = reader
        self.signatures    = get_signatures(images=images, videos=videos)
        self.chunk_sectors = chunk_sectors
        self.start_sector  = start_sector
        self.end_sector    = end_sector

    def scan(self) -> Iterator[CarvedFile]:
        sector_size = self.reader.sector_size
        overlap_bytes = max(len(s.header) + max(s.extra_checks.keys(), default=0) + 16
                            for s in self.signatures)
        prev_tail = b""

        for chunk_start, chunk_data in self.reader.iter_sectors(
            self.chunk_sectors, self.start_sector, self.end_sector
        ):
            window   = prev_tail + chunk_data
            win_base = chunk_start * sector_size - len(prev_tail)

            i = 0
            while i < len(window):
                for sig in self.signatures:
                    if _matches(sig, window, i):
                        abs_offset = win_base + i
                        carved = self._extract(sig, abs_offset)
                        if carved:
                            yield carved
                        i += sector_size
                        break
                else:
                    i += 1

            prev_tail = chunk_data[-overlap_bytes:] if len(chunk_data) >= overlap_bytes else chunk_data

    def _extract(self, sig: FileSignature, start_byte: int) -> CarvedFile | None:
        """Lee solo 1 MB para validar. Los datos se escriben en streaming al guardar."""
        probe_size = min(sig.max_size, 1 * 1024 * 1024)
        try:
            probe = self.reader.read_bytes_at(start_byte, probe_size)
        except OSError as e:
            log.debug(f"Error leyendo candidato en {start_byte:#x}: {e}")
            return None

        non_zero = sum(1 for b in probe[:256] if b != 0)
        if non_zero < 4:
            return None

        if sig.validator and not sig.validator(probe):
            return None

        estimator = SIZE_ESTIMATORS.get(sig.extension)
        estimated = estimator(probe) if estimator else 0

        if not estimated or estimated > sig.max_size:
            if sig.category in ("image", "raw"):
                estimated = min(sig.max_size, 50 * 1024 * 1024)
            else:
                estimated = min(sig.max_size, 2 * 1024 * 1024 * 1024)

        return CarvedFile(
            signature      = sig,
            start_byte     = start_byte,
            estimated_size = estimated,
            probe          = probe,
            reader         = self.reader,
        )
