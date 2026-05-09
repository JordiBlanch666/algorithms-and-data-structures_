"""
Acceso de bajo nivel a discos físicos y volúmenes lógicos en Windows.
Usa la API Win32 directamente mediante ctypes para leer sectores crudos.
Requiere: ejecutar como Administrador.
"""
import ctypes
import ctypes.wintypes as wt
import struct
from pathlib import Path


# ── Constantes Win32 ─────────────────────────────────────────────────────────
GENERIC_READ          = 0x80000000
FILE_SHARE_READ       = 0x00000001
FILE_SHARE_WRITE      = 0x00000002
OPEN_EXISTING         = 3
FILE_FLAG_NO_BUFFERING = 0x20000000
INVALID_HANDLE_VALUE  = ctypes.c_void_p(-1).value

IOCTL_DISK_GET_DRIVE_GEOMETRY_EX = 0x000700A0
IOCTL_STORAGE_QUERY_PROPERTY     = 0x002D1400

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class DISK_GEOMETRY_EX(ctypes.Structure):
    _fields_ = [
        ("Cylinders",         ctypes.c_int64),
        ("MediaType",         ctypes.c_uint),
        ("TracksPerCylinder", ctypes.c_ulong),
        ("SectorsPerTrack",   ctypes.c_ulong),
        ("BytesPerSector",    ctypes.c_ulong),
        ("DiskSize",          ctypes.c_int64),
        ("Data",              ctypes.c_byte * 1),
    ]


class DiskInfo:
    def __init__(self, path: str, sector_size: int, total_sectors: int, total_bytes: int):
        self.path = path
        self.sector_size = sector_size
        self.total_sectors = total_sectors
        self.total_bytes = total_bytes

    def __repr__(self) -> str:
        gb = self.total_bytes / (1024 ** 3)
        return (f"DiskInfo(path={self.path!r}, sector={self.sector_size}B, "
                f"sectors={self.total_sectors}, size={gb:.2f} GB)")


class DiskReader:
    """
    Lee sectores crudos de un disco físico o volumen lógico.

    Uso:
        with DiskReader(r"\\\\.\\PhysicalDrive0") as dr:
            sector = dr.read_sectors(0, 1)
    """

    def __init__(self, path: str):
        """
        path puede ser:
          - r'\\.\\PhysicalDrive0'   (disco físico)
          - r'\\.\\C:'               (volumen lógico)
        """
        self.path = path
        self._handle: int | None = None
        self.sector_size = 512
        self.total_bytes = 0
        self.total_sectors = 0

    # ── Context manager ───────────────────────────────────────────────────────
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()

    # ── Apertura / cierre ─────────────────────────────────────────────────────
    def open(self):
        handle = kernel32.CreateFileW(
            self.path,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_NO_BUFFERING,
            None,
        )
        if handle == INVALID_HANDLE_VALUE:
            err = ctypes.get_last_error()
            raise PermissionError(
                f"No se pudo abrir '{self.path}'. "
                f"Error Win32 {err}. ¿Ejecutas como Administrador?"
            )
        self._handle = handle
        self._read_geometry()

    def close(self):
        if self._handle is not None:
            kernel32.CloseHandle(self._handle)
            self._handle = None

    # ── Geometría del disco ───────────────────────────────────────────────────
    def _read_geometry(self):
        geo = DISK_GEOMETRY_EX()
        bytes_returned = wt.DWORD(0)
        ok = kernel32.DeviceIoControl(
            self._handle,
            IOCTL_DISK_GET_DRIVE_GEOMETRY_EX,
            None, 0,
            ctypes.byref(geo), ctypes.sizeof(geo),
            ctypes.byref(bytes_returned),
            None,
        )
        if ok:
            self.sector_size  = geo.BytesPerSector or 512
            self.total_bytes  = geo.DiskSize
            self.total_sectors = self.total_bytes // self.sector_size
        else:
            # Fallback para volúmenes pequeños / discos virtuales
            self.sector_size  = 512
            self.total_bytes  = self._probe_size()
            self.total_sectors = self.total_bytes // self.sector_size

    def _probe_size(self) -> int:
        """Mueve el puntero al final para estimar el tamaño."""
        high = wt.LONG(0)
        low  = kernel32.SetFilePointer(self._handle, 0, ctypes.byref(high), 2)  # FILE_END
        if low == 0xFFFFFFFF and ctypes.get_last_error():
            return 0
        return (high.value << 32) | (low & 0xFFFFFFFF)

    def info(self) -> DiskInfo:
        return DiskInfo(self.path, self.sector_size, self.total_sectors, self.total_bytes)

    # ── Lectura de sectores ───────────────────────────────────────────────────
    def read_sectors(self, start_sector: int, count: int = 1) -> bytes:
        """Lee `count` sectores consecutivos a partir de `start_sector`."""
        if self._handle is None:
            raise RuntimeError("El disco no está abierto.")

        offset = start_sector * self.sector_size
        size   = count * self.sector_size

        # SetFilePointer (compatible con discos > 2 GB)
        offset_low  = offset & 0xFFFFFFFF
        offset_high = offset >> 32
        high = wt.LONG(offset_high)
        result = kernel32.SetFilePointer(self._handle, wt.LONG(offset_low),
                                         ctypes.byref(high), 0)
        if result == 0xFFFFFFFF and ctypes.get_last_error():
            raise OSError(f"Error al posicionar sector {start_sector}: "
                          f"Win32 {ctypes.get_last_error()}")

        buf = ctypes.create_string_buffer(size)
        bytes_read = wt.DWORD(0)
        ok = kernel32.ReadFile(self._handle, buf, size, ctypes.byref(bytes_read), None)
        if not ok:
            raise OSError(f"Error de lectura en sector {start_sector}: "
                          f"Win32 {ctypes.get_last_error()}")

        return buf.raw[: bytes_read.value]

    def read_bytes_at(self, byte_offset: int, length: int) -> bytes:
        """Lee `length` bytes a partir de `byte_offset` (alineado a sector)."""
        sector_size  = self.sector_size
        start_sector = byte_offset // sector_size
        sector_off   = byte_offset % sector_size

        # Leer suficientes sectores para cubrir length + desplazamiento interno
        sectors_needed = (sector_off + length + sector_size - 1) // sector_size
        data = self.read_sectors(start_sector, sectors_needed)
        return data[sector_off: sector_off + length]

    # ── Iterador de sectores ──────────────────────────────────────────────────
    def iter_sectors(self, chunk_sectors: int = 2048, start: int = 0,
                     end: int | None = None):
        """
        Genera bloques de `chunk_sectors` sectores para escaneo secuencial.
        Yields: (sector_index, raw_bytes)
        """
        end = end or self.total_sectors
        current = start
        while current < end:
            count = min(chunk_sectors, end - current)
            try:
                data = self.read_sectors(current, count)
            except OSError:
                # Sector ilegible (bad sector) → saltar
                current += count
                continue
            yield current, data
            current += count


# ── Utilidades ────────────────────────────────────────────────────────────────
def list_physical_drives(max_drives: int = 16) -> list[str]:
    """Devuelve los discos físicos disponibles en el sistema."""
    found = []
    for i in range(max_drives):
        path = f"\\\\.\\PhysicalDrive{i}"
        h = kernel32.CreateFileW(
            path, GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None, OPEN_EXISTING, 0, None,
        )
        if h != INVALID_HANDLE_VALUE:
            kernel32.CloseHandle(h)
            found.append(path)
    return found


def list_logical_volumes() -> list[str]:
    """Devuelve letras de unidades lógicas accesibles (C:, D:, etc.)."""
    import string
    found = []
    for letter in string.ascii_uppercase:
        path = f"\\\\.\\{letter}:"
        h = kernel32.CreateFileW(
            path, GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None, OPEN_EXISTING, 0, None,
        )
        if h != INVALID_HANDLE_VALUE:
            kernel32.CloseHandle(h)
            found.append(path)
    return found
