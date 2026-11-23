# Autor: Jordi Y Blanch
"""
Reparador de archivos AVI (RIFF).

Corrige:
  1. Índice idx1 ausente o corrupto → se reconstruye escaneando el movi
  2. Tamaño RIFF incorrecto en la cabecera
  3. Tamaño del LIST movi incorrecto
  4. Cabecera avih con framecount incorrecto
"""
import struct
import logging
from pathlib import Path

from utils import read_u32_le, write_u32_le, CorruptionError, human_size

log = logging.getLogger(__name__)

# Tipos de chunk de datos válidos dentro de movi
# ##dc = video comprimido, ##db = video sin comprimir, ##wb = audio, ##tx = texto
def _is_data_chunk(fcc: bytes) -> bool:
    if len(fcc) != 4:
        return False
    # Los dos primeros bytes son el índice de stream (ascii dígito)
    if not (fcc[0:1].isdigit() or fcc[0] in range(0x30, 0x3A)):
        return False
    suffix = fcc[2:4]
    return suffix in (b"dc", b"db", b"wb", b"tx", b"pc", b"wc")


def _read_fourcc(data: bytes, offset: int) -> bytes:
    return data[offset:offset+4]


def _read_chunk(data: bytes, offset: int) -> tuple[bytes, int, int] | None:
    """
    Lee un chunk RIFF en `offset`.
    Devuelve (fourcc, tamaño_datos, offset_datos) o None si es inválido.
    El tamaño total del chunk es tamaño_datos + 8 (+ 1 si impar, por padding).
    """
    if offset + 8 > len(data):
        return None
    fcc  = data[offset:offset+4]
    size = read_u32_le(data, offset + 4)
    if size > len(data) - offset - 8 + 1:
        return None
    return fcc, size, offset + 8


def diagnose(path: Path) -> dict:
    data   = path.read_bytes()
    issues = []

    if len(data) < 12:
        return {"issues": ["too_small"], "file_size": len(data)}

    # Verificar firma RIFF
    if data[:4] != b"RIFF":
        issues.append("not_riff")
        return {"issues": issues, "file_size": len(data)}

    if data[8:12] != b"AVI ":
        issues.append("not_avi")

    riff_size = read_u32_le(data, 4)
    if riff_size != len(data) - 8:
        issues.append("riff_size_wrong")

    # Buscar idx1
    idx1_pos = data.rfind(b"idx1")
    if idx1_pos == -1:
        issues.append("idx1_missing")
    else:
        idx1_size = read_u32_le(data, idx1_pos + 4)
        if idx1_size == 0:
            issues.append("idx1_empty")

    return {"issues": issues, "file_size": len(data)}


def repair(src: Path, dst: Path) -> list[str]:
    data  = bytearray(src.read_bytes())
    fixes: list[str] = []

    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"AVI ":
        raise CorruptionError("No es un archivo AVI válido (firma RIFF ausente).")

    # ── 1. Localizar el LIST movi ─────────────────────────────────────────────
    movi_pos = -1
    pos = 12
    while pos + 12 <= len(data):
        fcc  = data[pos:pos+4]
        size = read_u32_le(data, pos + 4)
        if fcc == b"LIST" and data[pos+8:pos+12] == b"movi":
            movi_pos = pos
            break
        pos += 8 + size + (size % 2)
        if pos >= len(data):
            break

    if movi_pos == -1:
        raise CorruptionError("No se encontró el bloque movi. El archivo está muy dañado.")

    movi_data_start = movi_pos + 12   # después de LIST + size + 'movi'
    movi_size_field = movi_pos + 4

    # ── 2. Escanear movi para reconstruir idx1 ────────────────────────────────
    idx1_entries: list[tuple[bytes, int, int, int]] = []  # (fourcc, flags, offset_desde_movi, size)
    scan_pos = movi_data_start

    log.info("Escaneando chunks dentro de movi...")
    while scan_pos + 8 <= len(data):
        chunk = _read_chunk(data, scan_pos)
        if chunk is None:
            scan_pos += 2
            continue

        fcc, chunk_size, data_off = chunk

        if fcc == b"idx1":
            # Fin del movi
            break
        if fcc == b"LIST":
            scan_pos += 8 + chunk_size + (chunk_size % 2)
            continue
        if _is_data_chunk(fcc):
            offset_from_movi = scan_pos - movi_pos - 8
            flags = 0x10 if fcc[2:4] in (b"dc", b"db") else 0x00
            idx1_entries.append((fcc, flags, offset_from_movi, chunk_size))

        total_chunk = 8 + chunk_size + (chunk_size % 2)
        scan_pos += total_chunk

    log.info(f"Encontrados {len(idx1_entries)} chunks de datos.")

    # ── 3. Construir nuevo idx1 ───────────────────────────────────────────────
    idx1_data = bytearray()
    for fcc, flags, offset, size in idx1_entries:
        idx1_data += fcc
        idx1_data += struct.pack("<III", flags, offset, size)

    new_idx1 = b"idx1" + write_u32_le(len(idx1_data)) + bytes(idx1_data)
    fixes.append(f"idx1_rebuilt_{len(idx1_entries)}_entries")

    # ── 4. Corregir framecount en avih ────────────────────────────────────────
    avih_pos = data.find(b"avih")
    if avih_pos != -1 and avih_pos + 56 <= len(data):
        video_frames = sum(1 for fcc, _, _, _ in idx1_entries
                           if fcc[2:4] in (b"dc", b"db"))
        struct.pack_into("<I", data, avih_pos + 8 + 16, video_frames)
        fixes.append(f"avih_framecount_set_{video_frames}")

    # ── 5. Quitar idx1 viejo si existe ───────────────────────────────────────
    old_idx1 = data.find(b"idx1", movi_pos)
    if old_idx1 != -1:
        old_idx1_size = read_u32_le(data, old_idx1 + 4)
        del data[old_idx1: old_idx1 + 8 + old_idx1_size]
        fixes.append("idx1_old_removed")

    # ── 6. Recalcular tamaño de LIST movi ────────────────────────────────────
    movi_content_size = len(data) - movi_data_start + 4  # +4 por el 'movi' fourcc
    struct.pack_into("<I", data, movi_size_field, movi_content_size)
    fixes.append("movi_size_corrected")

    # ── 7. Añadir nuevo idx1 al final ─────────────────────────────────────────
    output = bytes(data) + new_idx1

    # ── 8. Corregir tamaño RIFF ───────────────────────────────────────────────
    output = bytearray(output)
    struct.pack_into("<I", output, 4, len(output) - 8)
    fixes.append("riff_size_corrected")

    dst.write_bytes(bytes(output))
    return fixes


def repair_avi(src: Path, dst: Path) -> dict:
    info   = diagnose(src)
    issues = info["issues"]

    if not issues:
        import shutil
        shutil.copy2(src, dst)
        return {"issues": [], "fixes": [], "success": True,
                "output_size": dst.stat().st_size}

    log.info(f"{src.name}: problemas → {issues}")
    try:
        fixes = repair(src, dst)
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}
    except CorruptionError as e:
        return {"issues": issues, "fixes": [], "success": False, "error": str(e),
                "output_size": 0}
