# Autor: Jordi Y Blanch
"""
Verificador rápido de archivos de vídeo recuperados.
Analiza la estructura interna sin necesidad de VLC ni ffmpeg.
Reporta cuáles tienen posibilidades reales de reproducirse.
"""
import struct
import sys
import os
import logging
from pathlib import Path
from dataclasses import dataclass

log = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm",
                    ".mpg", ".mpeg", ".vob", ".flv", ".wmv", ".3gp",
                    ".mts", ".m2ts"}

# ── Verificadores por formato ─────────────────────────────────────────────────

def _verify_mp4(data: bytes) -> tuple[bool, str]:
    pos = 0
    has_ftyp = has_moov = has_mdat = False
    while pos + 8 <= len(data):
        size = struct.unpack_from(">I", data, pos)[0]
        btype = data[pos+4:pos+8]
        if size == 0:
            break
        if size == 1:
            if pos + 16 > len(data):
                break
            size = struct.unpack_from(">Q", data, pos+8)[0]
        if btype == b"ftyp": has_ftyp = True
        if btype == b"moov": has_moov = True
        if btype == b"mdat": has_mdat = True
        if size < 8:
            break
        pos += size

    if has_moov and has_mdat:
        note = "✓ moov + mdat presentes"
        if not has_ftyp:
            note += " (sin ftyp — puede necesitar reparación)"
        return True, note
    if has_mdat and not has_moov:
        return False, "✗ falta moov (grabación interrumpida)"
    if not has_mdat:
        return False, "✗ falta mdat (sin datos de vídeo)"
    return False, "✗ estructura incompleta"


def _verify_avi(data: bytes) -> tuple[bool, str]:
    if data[:4] != b"RIFF" or data[8:12] != b"AVI ":
        return False, "✗ firma RIFF/AVI inválida"
    has_movi = b"LIST" in data[:4096] or b"movi" in data
    has_idx1 = b"idx1" in data
    if has_movi:
        note = "✓ estructura RIFF válida"
        if not has_idx1:
            note += " (sin idx1 — puede necesitar reparación)"
        return True, note
    return False, "✗ no se encontró el bloque movi"


def _verify_mkv(data: bytes) -> tuple[bool, str]:
    if data[:4] != b"\x1A\x45\xDF\xA3":
        return False, "✗ firma EBML inválida"
    has_segment = b"\x18\x53\x80\x67" in data[:256]
    has_cluster = b"\x1F\x43\xB6\x75" in data
    if has_cluster:
        return True, "✓ EBML válido con clusters de datos"
    if has_segment:
        return False, "✗ segmento presente pero sin clusters (sin datos)"
    return False, "✗ estructura EBML incompleta"


def _verify_mpg(data: bytes) -> tuple[bool, str]:
    pack_count = data.count(b"\x00\x00\x01\xBA")
    seq_count  = data.count(b"\x00\x00\x01\xB3")
    if pack_count >= 10:
        return True, f"✓ {pack_count} pack headers, {seq_count} sequence headers"
    if pack_count >= 2:
        return False, f"⚠ solo {pack_count} packs — posiblemente incompleto"
    if seq_count >= 1:
        return False, f"⚠ MPEG-1 con {seq_count} sequence headers pero pocos packs"
    return False, "✗ no se encontraron paquetes MPEG válidos"


def _verify_flv(data: bytes) -> tuple[bool, str]:
    if data[:3] != b"FLV":
        return False, "✗ firma FLV inválida"
    return True, "✓ firma FLV válida"


def _verify_wmv(data: bytes) -> tuple[bool, str]:
    if data[:8] != b"\x30\x26\xB2\x75\x8E\x66\xCF\x11":
        return False, "✗ firma ASF/WMV inválida"
    return True, "✓ firma ASF/WMV válida"


def _verify_mts(data: bytes) -> tuple[bool, str]:
    # Verificar que cada 188 bytes hay un sync byte 0x47 (al menos 10 paquetes)
    if len(data) < 188 * 10:
        return False, "✗ archivo demasiado pequeño para MTS"
    valid_syncs = sum(1 for i in range(10) if data[i * 188] == 0x47)
    if valid_syncs >= 8:
        return True, f"✓ MPEG-TS válido ({valid_syncs}/10 sync bytes correctos)"
    return False, f"✗ falso positivo MTS ({valid_syncs}/10 sync bytes) — no es AVCHD real"


VERIFIERS = {
    ".mp4": _verify_mp4, ".mov": _verify_mp4, ".m4v": _verify_mp4,
    ".3gp": _verify_mp4,
    ".avi": _verify_avi,
    ".mkv": _verify_mkv, ".webm": _verify_mkv,
    ".mpg": _verify_mpg, ".mpeg": _verify_mpg, ".vob": _verify_mpg,
    ".flv": _verify_flv,
    ".wmv": _verify_wmv,
    ".mts": _verify_mts, ".m2ts": _verify_mts,
}

PROBE_SIZE = 5 * 1024 * 1024   # leer solo los primeros 5 MB para verificar


# ── Resultado ─────────────────────────────────────────────────────────────────
@dataclass
class VerifyResult:
    path: Path
    size_mb: float
    viable: bool
    note: str

    def line(self) -> str:
        icon = "✓" if self.viable else "✗"
        return f"  {icon}  {self.size_mb:6.1f} MB  {self.path.name:<45}  {self.note}"


# ── Lógica principal ──────────────────────────────────────────────────────────
def verify_file(path: Path) -> VerifyResult:
    ext = path.suffix.lower()
    size_mb = path.stat().st_size / (1024 * 1024)

    if ext not in VERIFIERS:
        return VerifyResult(path, size_mb, False, "formato no soportado")

    try:
        with open(path, "rb") as f:
            data = f.read(PROBE_SIZE)
    except OSError as e:
        return VerifyResult(path, size_mb, False, f"error de lectura: {e}")

    if len(data) < 16:
        return VerifyResult(path, size_mb, False, "✗ archivo demasiado pequeño")

    viable, note = VERIFIERS[ext](data)
    return VerifyResult(path, size_mb, viable, note)


def verify_folder(folder: Path) -> list[VerifyResult]:
    files = sorted(
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    )
    return [verify_file(f) for f in files]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    p = argparse.ArgumentParser(
        prog="verify",
        description="Verifica qué archivos de vídeo recuperados son reproducibles",
    )
    p.add_argument("input", help="Archivo o carpeta a verificar")
    p.add_argument("--viable-only", action="store_true",
                   help="Mostrar solo los archivos viables")
    p.add_argument("--copy-viable", metavar="DESTINO",
                   help="Copiar los viables a esta carpeta")
    args = p.parse_args()

    target = Path(args.input)
    if not target.exists():
        print(f"✗ No existe: {target}")
        sys.exit(1)

    print(f"\nAnalizando: {target}\n")

    if target.is_file():
        results = [verify_file(target)]
    else:
        results = verify_folder(target)

    if not results:
        print("No se encontraron archivos de vídeo.")
        return

    viables  = [r for r in results if r.viable]
    invalids = [r for r in results if not r.viable]

    print(f"{'─'*80}")
    print(f"  {'MB':>6}  {'Archivo':<45}  Resultado")
    print(f"{'─'*80}")

    if not args.viable_only:
        for r in invalids:
            print(r.line())

    for r in viables:
        print(r.line())

    print(f"{'─'*80}")
    print(f"  Total: {len(results)}  |  Viables: {len(viables)}  |  Corruptos: {len(invalids)}")
    print(f"{'─'*80}\n")

    if args.copy_viable and viables:
        import shutil
        dest = Path(args.copy_viable)
        dest.mkdir(parents=True, exist_ok=True)
        for r in viables:
            shutil.copy2(r.path, dest / r.path.name)
        print(f"  {len(viables)} archivo(s) viable(s) copiados a: {dest}\n")


if __name__ == "__main__":
    main()
