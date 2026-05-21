# Autor: Jordi Y Blanch
"""
Reparador de archivos MP4 / MOV / M4V.

Corrige los problemas más comunes:
  1. Tamaños de box incorrectos
  2. átomo moov ausente o al final del archivo (grabación interrumpida)
  3. Atom ftyp faltante
  4. Archivo truncado con mdat incompleto
  5. Reordenación de boxes: ftyp → moov → mdat (streaming-friendly)
"""
import struct
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from utils import (
    read_u32_be, read_u64_be, write_u32_be, write_u64_be,
    fourcc, CorruptionError, backup_file, human_size
)

log = logging.getLogger(__name__)

# Boxes conocidos del estándar ISO BMFF / QuickTime
KNOWN_BOXES = {
    "ftyp", "moov", "mdat", "free", "skip", "wide", "pnot",
    "mvhd", "trak", "tkhd", "mdia", "mdhd", "hdlr", "minf",
    "dinf", "dref", "stbl", "stsd", "stts", "stsc", "stsz",
    "stco", "co64", "stss", "ctts", "smhd", "vmhd", "nmhd",
    "udta", "meta", "ilst", "meco", "uuid", "edts", "elst",
    "mvex", "mehd", "trex", "moof", "mfhd", "traf", "tfhd",
    "trun", "mfra", "tfra", "mfro", "sidx", "ssix",
}

# Tipos ftyp compatibles
FTYP_BRANDS = {
    b"isom", b"iso2", b"mp41", b"mp42", b"M4V ", b"M4A ",
    b"qt  ", b"avc1", b"MSNV", b"f4v ", b"crx ", b"heic",
}


@dataclass
class Box:
    offset: int      # posición en el archivo
    size: int        # tamaño total incluyendo cabecera
    box_type: str    # fourcc
    header_size: int # 8 o 16 (si usa tamaño de 64 bits)
    data_offset: int # offset donde empiezan los datos del box


def _parse_box_header(data: bytes, offset: int) -> Box | None:
    """
    Lee la cabecera de un box ISO BMFF en `offset`.
    Devuelve None si los bytes no forman un box válido.
    """
    if offset + 8 > len(data):
        return None

    size = read_u32_be(data, offset)
    btype = fourcc(data, offset + 4)

    if btype not in KNOWN_BOXES and not btype.isprintable():
        return None

    if size == 1:
        # Tamaño de 64 bits
        if offset + 16 > len(data):
            return None
        size = read_u64_be(data, offset + 8)
        header_size = 16
        data_offset = offset + 16
    elif size == 0:
        # Tamaño hasta fin de archivo
        size = len(data) - offset
        header_size = 8
        data_offset = offset + 8
    else:
        header_size = 8
        data_offset = offset + 8

    if size < header_size or offset + size > len(data) + 1:
        return None

    return Box(offset=offset, size=size, box_type=btype,
               header_size=header_size, data_offset=data_offset)


def _scan_boxes(data: bytes, start: int = 0, end: int | None = None) -> list[Box]:
    """Escanea boxes desde `start` hasta `end` y devuelve los válidos."""
    end = end or len(data)
    boxes = []
    pos = start
    consecutive_fails = 0

    while pos < end:
        box = _parse_box_header(data, pos)
        if box is None:
            consecutive_fails += 1
            if consecutive_fails > 32:
                break
            pos += 4
            continue
        consecutive_fails = 0
        boxes.append(box)
        next_pos = pos + box.size
        if next_pos <= pos:
            break
        pos = next_pos

    return boxes


def _find_moov_by_scan(data: bytes) -> int:
    """Busca la firma 'moov' en todo el archivo cuando el parseo normal falla."""
    pos = 0
    while pos < len(data) - 8:
        if data[pos+4:pos+8] == b"moov":
            candidate_size = read_u32_be(data, pos)
            if 8 <= candidate_size <= len(data) - pos:
                return pos
        pos += 4
    return -1


def _build_ftyp() -> bytes:
    """Genera un átomo ftyp mínimo compatible con reproductores estándar."""
    compatible = b"isom" + b"iso2" + b"avc1" + b"mp41"
    size = 8 + 4 + 4 + len(compatible)   # header + major + minor + compat
    return write_u32_be(size) + b"ftyp" + b"isom" + b"\x00\x02\x00\x00" + compatible


def _fix_stco_offsets(moov_data: bytes, delta: int) -> bytes:
    """
    Ajusta los offsets absolutos de los chunk offset tables (stco/co64)
    dentro del blob del moov, sumando `delta` bytes.
    Necesario cuando reordenamos ftyp/moov antes del mdat.
    """
    result = bytearray(moov_data)
    pos = 0

    while pos < len(result) - 8:
        size = struct.unpack_from(">I", result, pos)[0]
        btype = result[pos+4:pos+8]

        if btype == b"stco" and size >= 20:
            # stco: version(1) + flags(3) + entry_count(4) + entries(4*n)
            entry_count = struct.unpack_from(">I", result, pos + 12)[0]
            for i in range(entry_count):
                eoff = pos + 16 + i * 4
                if eoff + 4 <= len(result):
                    old = struct.unpack_from(">I", result, eoff)[0]
                    struct.pack_into(">I", result, eoff, old + delta)

        elif btype == b"co64" and size >= 20:
            entry_count = struct.unpack_from(">I", result, pos + 12)[0]
            for i in range(entry_count):
                eoff = pos + 16 + i * 8
                if eoff + 8 <= len(result):
                    old = struct.unpack_from(">Q", result, eoff)[0]
                    struct.pack_into(">Q", result, eoff, old + delta)

        if size <= 0:
            break
        pos += size

    return bytes(result)


# ── Diagnóstico ───────────────────────────────────────────────────────────────
def diagnose(path: Path) -> dict:
    """
    Analiza un MP4 y devuelve un diccionario con los problemas detectados.
    """
    data = path.read_bytes()
    issues = []
    info   = {}

    boxes = _scan_boxes(data)
    types = {b.box_type: b for b in boxes}

    info["boxes_found"] = [b.box_type for b in boxes]
    info["file_size"]   = len(data)

    if "ftyp" not in types:
        issues.append("ftyp_missing")
    if "moov" not in types:
        # Intento de búsqueda por firma
        moov_pos = _find_moov_by_scan(data)
        if moov_pos >= 0:
            issues.append("moov_corrupted_size")
        else:
            issues.append("moov_missing")
    if "mdat" not in types:
        issues.append("mdat_missing")

    # ¿moov está después de mdat? (grabación interrumpida)
    if "moov" in types and "mdat" in types:
        if types["moov"].offset > types["mdat"].offset:
            issues.append("moov_after_mdat")

    # ¿Tamaño del último box desborda el archivo?
    if boxes:
        last = boxes[-1]
        if last.offset + last.size > len(data) + 512:
            issues.append("truncated")

    info["issues"] = issues
    return info


# ── Reparación ────────────────────────────────────────────────────────────────
def repair(src: Path, dst: Path) -> list[str]:
    """
    Repara `src` y guarda el resultado en `dst`.
    Devuelve lista de reparaciones aplicadas.
    """
    data  = src.read_bytes()
    fixes: list[str] = []
    boxes = _scan_boxes(data)
    types = {b.box_type: b for b in boxes}

    # ── 1. moov con tamaño incorrecto → buscar por firma ─────────────────────
    if "moov" not in types:
        moov_pos = _find_moov_by_scan(data)
        if moov_pos >= 0:
            log.info("moov encontrado por firma — corrigiendo tamaño")
            # Recalcular tamaño hasta el próximo box reconocible o fin de archivo
            remaining = len(data) - moov_pos
            corrected = bytearray(data)
            struct.pack_into(">I", corrected, moov_pos, remaining)
            data  = bytes(corrected)
            boxes = _scan_boxes(data)
            types = {b.box_type: b for b in boxes}
            fixes.append("moov_size_corrected")

    if "moov" not in types and "mdat" not in types:
        raise CorruptionError("No se encontró moov ni mdat. El archivo está demasiado dañado.")

    # ── 2. ftyp faltante → insertar uno genérico ──────────────────────────────
    needs_ftyp = "ftyp" not in types
    ftyp_data  = data[types["ftyp"].offset: types["ftyp"].offset + types["ftyp"].size] \
                 if not needs_ftyp else _build_ftyp()
    if needs_ftyp:
        fixes.append("ftyp_inserted")

    # ── 3. Reordenar: ftyp → moov → mdat ─────────────────────────────────────
    if "moov" in types and "mdat" in types:
        moov_box = types["moov"]
        mdat_box = types["mdat"]
        ftyp_box = types.get("ftyp")

        moov_data = data[moov_box.offset: moov_box.offset + moov_box.size]
        mdat_data = data[mdat_box.offset: mdat_box.offset + mdat_box.size]

        new_ftyp_size  = len(ftyp_data)
        new_moov_start = new_ftyp_size

        # El mdat empezará justo después del nuevo moov
        new_mdat_start = new_ftyp_size + len(moov_data)

        old_mdat_start = mdat_box.offset
        delta = new_mdat_start - old_mdat_start
        if delta != 0:
            moov_data = _fix_stco_offsets(moov_data, delta)
            fixes.append(f"chunk_offsets_adjusted_by_{delta:+d}")

        # Agregar resto de boxes (free, udta, etc.) que no sean ftyp/moov/mdat
        extra = b"".join(
            data[b.offset: b.offset + b.size]
            for b in boxes
            if b.box_type not in ("ftyp", "moov", "mdat")
        )

        output = ftyp_data + moov_data + mdat_data + extra
        fixes.append("boxes_reordered_ftyp_moov_mdat")
    else:
        output = data
        fixes.append("partial_repair_no_reorder")

    dst.write_bytes(output)
    return fixes


# ── API pública ───────────────────────────────────────────────────────────────
def repair_mp4(src: Path, dst: Path) -> dict:
    """
    Punto de entrada principal.
    Devuelve dict con 'issues', 'fixes', 'success', 'output_size'.
    """
    info   = diagnose(src)
    issues = info["issues"]

    if not issues:
        log.info(f"{src.name}: no se detectaron problemas graves.")
        import shutil
        shutil.copy2(src, dst)
        return {"issues": [], "fixes": [], "success": True,
                "output_size": dst.stat().st_size}

    log.info(f"{src.name}: problemas detectados → {issues}")
    try:
        fixes = repair(src, dst)
        return {"issues": issues, "fixes": fixes, "success": True,
                "output_size": dst.stat().st_size}
    except CorruptionError as e:
        return {"issues": issues, "fixes": [], "success": False, "error": str(e),
                "output_size": 0}
