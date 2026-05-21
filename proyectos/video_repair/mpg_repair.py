# Autor: Jordi Y Blanch
"""
Reparador de archivos MPEG-1 / MPEG-2 (.mpg, .mpeg, .vob).

Corrige:
  1. Rellena paquetes corruptos con paquetes nulos válidos
  2. Reconstruye la cabecera Pack si falta
  3. Elimina bytes basura entre paquetes
  4. Trunca el archivo en el último paquete válido
"""
import struct
import logging
from pathlib import Path

from utils import CorruptionError, human_size

log = logging.getLogger(__name__)

# Firmas de inicio de paquete MPEG-2 PS
PACK_START  = b"\x00\x00\x01\xBA"   # Pack header
VIDEO_START = b"\x00\x00\x01\xB3"   # Sequence header (MPEG-1 video)
PES_STARTS  = {0xE0, 0xE1, 0xE2, 0xE3,  # video streams
               0xC0, 0xC1, 0xC2, 0xC3,  # audio streams
               0xBD, 0xBE, 0xBF}         # private / padding

# Paquete nulo MPEG-2 PS (relleno válido de 2048 bytes)
NULL_PACK = PACK_START + b"\x00" * 2044


def _is_pack_header(data: bytes, pos: int) -> bool:
    if pos + 4 > len(data):
        return False
    return data[pos:pos+4] == PACK_START


def _is_pes_header(data: bytes, pos: int) -> bool:
    if pos + 4 > len(data):
        return False
    if data[pos:pos+3] != b"\x00\x00\x01":
        return False
    return data[pos+3] in PES_STARTS


def _next_sync(data: bytes, pos: int) -> int:
    """Busca el próximo Pack o PES header desde pos. Devuelve -1 si no hay."""
    while pos + 4 <= len(data):
        if data[pos:pos+3] == b"\x00\x00\x01":
            if data[pos+3] == 0xBA or data[pos+3] in PES_STARTS:
                return pos
        pos += 1
    return -1


def _read_pes_size(data: bytes, pos: int) -> int:
    """Devuelve el tamaño total del PES packet (cabecera + payload)."""
    if pos + 6 > len(data):
        return 0
    payload_len = struct.unpack_from(">H", data, pos + 4)[0]
    return 6 + payload_len if payload_len > 0 else 0


def _find_real_end(data: bytes) -> int:
    """
    Encuentra el offset real donde termina el contenido MPEG válido.
    Busca el end code 0x000001B9 o el último pack seguido de zona de ceros/basura.
    """
    # Caso 1: end code explícito
    end_code = data.rfind(b"\x00\x00\x01\xB9")
    if end_code != -1 and end_code > len(data) // 2:
        return end_code + 4

    # Caso 2: encontrar el último pack válido seguido de zona sin packs
    # Escanear desde el final hacia atrás buscando el último PACK_START
    # seguido de al menos 12 bytes coherentes
    search_window = min(len(data), 50 * 1024 * 1024)  # buscar en los últimos 50 MB
    tail = data[len(data) - search_window:]
    tail_offset = len(data) - search_window

    last_valid = -1
    pos = 0
    while pos < len(tail) - 4:
        idx = tail.find(PACK_START, pos)
        if idx == -1:
            break
        # Verificar que el siguiente sync existe dentro de 2 MB (paquete razonable)
        next_sync = tail.find(b"\x00\x00\x01", idx + 4)
        if next_sync != -1 and next_sync - idx < 2 * 1024 * 1024:
            last_valid = tail_offset + next_sync
        pos = idx + 4

    return last_valid if last_valid > len(data) // 4 else len(data)


def diagnose(path: Path) -> dict:
    data   = path.read_bytes()
    issues = []

    if len(data) < 12:
        return {"issues": ["too_small"], "file_size": len(data)}

    if data[:4] not in (PACK_START, VIDEO_START):
        if b"\x00\x00\x01\xBA" not in data[:2048]:
            issues.append("no_mpeg_signature")

    pack_count = data.count(PACK_START)
    if pack_count == 0:
        issues.append("no_pack_headers")
    elif pack_count < 3:
        issues.append("very_few_packs")

    # Detectar si el archivo tiene cola de basura (carving sin fin conocido)
    real_end = _find_real_end(data)
    if real_end < len(data) - 1024:
        issues.append(f"garbage_tail_{len(data) - real_end}_bytes")

    # Verificar si termina abruptamente
    last_pack = data.rfind(PACK_START)
    if last_pack != -1 and last_pack > len(data) - 12:
        issues.append("truncated")

    return {"issues": issues, "file_size": len(data),
            "pack_count": pack_count, "real_end": real_end}


def repair(src: Path, dst: Path) -> list[str]:
    data  = src.read_bytes()
    fixes: list[str] = []

    # ── 1. Encontrar primer sync válido ───────────────────────────────────────
    first_sync = _next_sync(data, 0)
    if first_sync == -1:
        raise CorruptionError("No se encontraron paquetes MPEG válidos.")

    if first_sync > 0:
        data  = data[first_sync:]
        fixes.append(f"stripped_{first_sync}_bytes_before_first_sync")

    # ── 2. Reconstruir stream eliminando zonas corruptas ─────────────────────
    output  = bytearray()
    pos     = 0
    good    = 0
    skipped = 0

    while pos < len(data):
        if _is_pack_header(data, pos):
            # Pack de 2048 bytes (sector DVD) o tamaño variable
            # Intentar leer hasta el próximo pack
            next_pos = _next_sync(data, pos + 4)
            if next_pos == -1:
                # Último paquete — copiar hasta el final
                output += data[pos:]
                good += 1
                break

            chunk = data[pos:next_pos]
            # Validar que el chunk no sea demasiado grande (>= 1 MB = basura)
            if len(chunk) <= 1024 * 1024:
                output += chunk
                good += 1
            else:
                # Zona corrupta grande → insertar pack nulo y saltar
                output += NULL_PACK
                skipped += 1

            pos = next_pos

        elif _is_pes_header(data, pos):
            size = _read_pes_size(data, pos)
            if size > 0 and pos + size <= len(data):
                output += data[pos:pos+size]
                good += 1
                pos  += size
            else:
                pos += 1

        else:
            # Byte basura → saltar
            pos += 1
            skipped += 1

    if good == 0:
        raise CorruptionError("No se encontraron paquetes recuperables.")

    fixes.append(f"reconstructed_{good}_packets")
    if skipped:
        fixes.append(f"skipped_{skipped}_corrupt_bytes")

    # ── 3. Añadir end code MPEG si falta ─────────────────────────────────────
    if not bytes(output).endswith(b"\x00\x00\x01\xB9"):
        output += b"\x00\x00\x01\xB9"
        fixes.append("end_code_added")

    dst.write_bytes(bytes(output))
    return fixes


def repair_mpg(src: Path, dst: Path) -> dict:
    info   = diagnose(src)
    issues = info["issues"]
    real_end = info.get("real_end", src.stat().st_size)

    # Si no hay otros problemas pero sí cola de basura, truncar simplemente
    garbage_issues = [i for i in issues if i.startswith("garbage_tail")]
    other_issues   = [i for i in issues if not i.startswith("garbage_tail")]

    if garbage_issues and not other_issues:
        data = src.read_bytes()
        truncated = data[:real_end]
        if not truncated.endswith(b"\x00\x00\x01\xB9"):
            truncated += b"\x00\x00\x01\xB9"
        dst.write_bytes(truncated)
        saved = src.stat().st_size - real_end
        fixes = [f"truncated_garbage_{saved // (1024*1024)}_MB"]
        log.info(f"{src.name}: eliminados {saved // (1024*1024)} MB de basura al final")
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}

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
        return {"issues": issues, "fixes": [], "success": False,
                "error": str(e), "output_size": 0}
