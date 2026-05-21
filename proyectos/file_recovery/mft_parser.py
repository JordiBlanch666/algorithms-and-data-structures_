# Autor: Jordi Y Blanch
"""
Parser de la Master File Table (MFT) de NTFS.
Detecta entradas de archivos eliminados (flag de "en uso" = 0) con
extensiones de imagen y vídeo para recuperarlos.

Formato MFT:
  - Cada entrada ocupa 1024 bytes (por defecto)
  - Empieza con la firma b"FILE"
  - El campo Flags indica si el archivo está activo o eliminado
"""
import struct
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from disk_reader import DiskReader

log = logging.getLogger(__name__)


# ── Constantes NTFS ───────────────────────────────────────────────────────────
MFT_SIGNATURE          = b"FILE"
MFT_RECORD_SIZE        = 1024    # bytes por entrada MFT
MFT_FLAG_IN_USE        = 0x0001  # archivo activo
MFT_FLAG_DIRECTORY     = 0x0002

# Tipos de atributo NTFS relevantes
ATTR_STANDARD_INFORMATION = 0x10
ATTR_FILE_NAME            = 0x30
ATTR_DATA                 = 0x80
ATTR_END                  = 0xFFFFFFFF

# Extensiones objetivo
TARGET_EXTENSIONS = {
    # imágenes
    "jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff",
    "webp", "heic", "heif",
    # RAW
    "cr2", "cr3", "nef", "arw", "dng", "orf", "rw2",
    # vídeo
    "mp4", "m4v", "mov", "avi", "mkv", "wmv", "flv",
    "mpg", "mpeg", "3gp", "mts", "m2ts", "vob",
}


# ── Estructuras de datos ──────────────────────────────────────────────────────
@dataclass
class MFTEntry:
    mft_index: int
    filename: str
    extension: str
    size: int          # bytes lógicos del atributo $DATA
    is_deleted: bool
    data_runs: list[tuple[int, int]]  # (cluster_offset, cluster_count)


# ── Funciones de decodificación MFT ──────────────────────────────────────────
def _apply_fixup(raw: bytes) -> bytes:
    """Aplica el Update Sequence Array (USA) para corregir sectores MFT."""
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
    Devuelve (nombre_archivo, tamaño_lógico) desde un atributo $FILE_NAME.
    Offset 64 = tamaño lógico asignado, offset 80 = longitud del nombre.
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
    Decodifica data runs NTFS. Devuelve lista de (cluster_inicio, num_clusters).
    cluster_inicio = -1 indica datos no-residentes sin posición (sparse).
    """
    runs = []
    pos  = 0
    vcn  = 0
    while pos < len(run_bytes):
        header = run_bytes[pos]
        if header == 0:
            break
        len_bytes = header & 0x0F   # nibble bajo: bytes de longitud
        off_bytes = header >> 4     # nibble alto: bytes de offset
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
        # El offset es con signo (relativo al run anterior)
        run_offset = int.from_bytes(run_offset_raw, "little", signed=False)
        if run_offset_raw and (run_offset_raw[-1] & 0x80):
            run_offset -= 1 << (off_bytes * 8)
        vcn += run_offset

        runs.append((vcn, run_len))

    return runs


def _parse_mft_record(raw: bytes, mft_index: int) -> MFTEntry | None:
    """Intenta parsear una entrada MFT y devuelve MFTEntry o None si no es válida."""
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
            if name and "$" not in name:   # ignorar metaarchivos del sistema
                filename  = name
                file_size = size

        elif attr_type == ATTR_DATA and non_resident:
            # Leer data runs desde el encabezado de atributo no-residente
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


# ── Clase principal ───────────────────────────────────────────────────────────
class MFTParser:
    """
    Lee y parsea la MFT de un volumen NTFS para encontrar archivos
    de imagen/vídeo eliminados.

    Uso:
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
        Lee el Boot Sector (sector 0) de NTFS para obtener el offset del $MFT.
        Devuelve el offset en bytes o -1 si no es NTFS.
        """
        boot = self.reader.read_sectors(0, 1)
        if len(boot) < 512:
            return -1

        # Firma OEM NTFS en offset 3
        if boot[3:11] != b"NTFS    ":
            log.warning("El volumen no parece ser NTFS (firma OEM no encontrada).")
            return -1

        bytes_per_sector  = struct.unpack_from("<H", boot, 11)[0]
        sectors_per_clust = boot[13]
        mft_cluster       = struct.unpack_from("<Q", boot, 48)[0]

        self.sector_size  = bytes_per_sector or 512
        self.cluster_size = sectors_per_clust * self.sector_size

        mft_byte_offset = mft_cluster * self.cluster_size
        log.info(f"MFT encontrada en offset {mft_byte_offset:#x} "
                 f"(cluster {mft_cluster})")
        return mft_byte_offset

    def find_deleted(self, include_active: bool = False) -> Iterator[MFTEntry]:
        """
        Itera sobre todas las entradas MFT y devuelve archivos eliminados
        (o activos si include_active=True) con extensiones de imagen/vídeo.
        """
        mft_offset = self._find_mft_start()
        if mft_offset < 0:
            log.error("No se pudo localizar la MFT. ¿Es un volumen NTFS?")
            return

        index = 0
        offset = mft_offset

        while offset + MFT_RECORD_SIZE <= self.reader.total_bytes:
            try:
                raw = self.reader.read_bytes_at(offset, MFT_RECORD_SIZE)
            except OSError as e:
                log.debug(f"Error leyendo MFT[{index}]: {e}")
                offset += MFT_RECORD_SIZE
                index  += 1
                continue

            if raw[:4] != MFT_SIGNATURE:
                # Fin de la MFT o zona corrupta
                break

            entry = _parse_mft_record(raw, index)
            if entry and (entry.is_deleted or include_active):
                yield entry

            offset += MFT_RECORD_SIZE
            index  += 1

    def read_file_data(self, entry: MFTEntry) -> bytes:
        """
        Reconstruye el contenido de un archivo usando sus data runs.
        Devuelve bytes (puede estar incompleto si hay sectores dañados).
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
                log.warning(f"Sector dañado al leer '{entry.filename}': {e}")
                chunks.append(b"\x00" * to_read)
                total_read += to_read

        return b"".join(chunks)[: entry.size]
