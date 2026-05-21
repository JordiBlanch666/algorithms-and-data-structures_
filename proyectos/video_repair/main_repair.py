# Autor: Jordi Y Blanch
"""
VideoRepair — Reparador de vídeos corruptos (Python puro, sin dependencias)
===========================================================================

Formatos soportados: MP4, MOV, M4V, AVI, MKV, WebM

Uso:
  python main_repair.py --input video.mp4 --output reparados/
  python main_repair.py --input carpeta_corruptos/ --output reparados/
  python main_repair.py --diagnose video.mp4
"""
import argparse
import logging
import sys
from pathlib import Path

from repair_engine import RepairEngine, SUPPORTED
from mp4_repair import diagnose as diagnose_mp4
from avi_repair import diagnose as diagnose_avi
from mkv_repair import diagnose as diagnose_mkv
from utils import human_size


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


DIAGNOSERS = {
    ".mp4": diagnose_mp4, ".m4v": diagnose_mp4, ".mov": diagnose_mp4,
    ".avi": diagnose_avi,
    ".mkv": diagnose_mkv, ".webm": diagnose_mkv,
}


def _run_diagnose(path: Path):
    ext = path.suffix.lower()
    if ext not in DIAGNOSERS:
        print(f"✗ Formato no soportado: {ext}")
        return

    info = DIAGNOSERS[ext](path)
    issues = info.get("issues", [])
    size   = info.get("file_size", 0)

    print(f"\n{'─'*55}")
    print(f"  Diagnóstico: {path.name}")
    print(f"{'─'*55}")
    print(f"  Tamaño    : {human_size(size)}")
    print(f"  Formato   : {ext.lstrip('.')}")

    if not issues:
        print("  Estado    : ✓ No se detectaron problemas")
    else:
        print(f"  Problemas : {len(issues)}")
        for issue in issues:
            print(f"    • {_issue_description(issue)}")
    print(f"{'─'*55}\n")


def _issue_description(issue: str) -> str:
    descriptions = {
        "ftyp_missing":         "Falta el átomo ftyp (tipo de archivo)",
        "moov_missing":         "Falta el átomo moov (metadatos — grabación interrumpida)",
        "moov_corrupted_size":  "El átomo moov tiene tamaño incorrecto",
        "moov_after_mdat":      "El moov está al final (puede causar carga lenta)",
        "mdat_missing":         "Falta el bloque mdat (datos de vídeo)",
        "truncated":            "El archivo parece estar truncado (incompleto)",
        "riff_size_wrong":      "Tamaño RIFF incorrecto en la cabecera",
        "idx1_missing":         "Falta el índice idx1 (AVI no seekable)",
        "idx1_empty":           "El índice idx1 está vacío",
        "not_riff":             "No es un archivo RIFF válido",
        "not_avi":              "El contenedor RIFF no contiene AVI",
        "not_ebml":             "No se encontró el encabezado EBML (MKV/WebM)",
        "segment_missing":      "No se encontró el Segment EBML",
        "segment_size_unknown": "El Segment tiene tamaño desconocido (normal en streams)",
        "seekhead_missing":     "Falta el SeekHead (MKV no seekable)",
        "cues_missing":         "Faltan las Cues (navegación degradada)",
        "info_missing":         "Falta el elemento Info",
        "too_small":            "El archivo es demasiado pequeño para ser válido",
        "unsupported_format":   "Formato de archivo no soportado",
    }
    return descriptions.get(issue, issue)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="videorepair",
        description="Reparador de vídeos corruptos — MP4, AVI, MKV (Python puro)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main_repair.py --diagnose video.mp4
  python main_repair.py --input video.mp4 --output C:\\Reparados
  python main_repair.py --input C:\\Recuperados --output C:\\Reparados
  python main_repair.py --input carpeta/ --output reparados/ --verbose
""",
    )

    p.add_argument("--diagnose", metavar="ARCHIVO",
                   help="Analizar un archivo y mostrar problemas sin reparar")
    p.add_argument("--input", "-i", metavar="ARCHIVO_O_CARPETA",
                   help="Archivo o carpeta con vídeos a reparar")
    p.add_argument("--output", "-o", metavar="CARPETA",
                   help="Carpeta donde guardar los vídeos reparados")
    p.add_argument("--no-backup", action="store_true",
                   help="No crear copia .bak del archivo original")
    p.add_argument("--overwrite", action="store_true",
                   help="Sobreescribir si ya existe el archivo reparado")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Mostrar log detallado")
    return p


def main():
    parser = _build_parser()
    args   = parser.parse_args()
    _setup_logging(args.verbose)

    # ── Modo diagnóstico ──────────────────────────────────────────────────────
    if args.diagnose:
        _run_diagnose(Path(args.diagnose))
        return

    # ── Modo reparación ───────────────────────────────────────────────────────
    if not args.input or not args.output:
        parser.error("Se requieren --input y --output (o usa --diagnose)")

    src = Path(args.input)
    dst = Path(args.output)

    if not src.exists():
        print(f"✗ No existe: {src}")
        sys.exit(1)

    engine = RepairEngine(
        output_dir = dst,
        backup     = not args.no_backup,
        overwrite  = args.overwrite,
    )

    print(f"\n{'─'*55}")
    print(f"  VideoRepair — Reparador de vídeos")
    print(f"{'─'*55}")
    print(f"  Entrada : {src}")
    print(f"  Salida  : {dst}")
    print(f"  Formatos: {', '.join(SUPPORTED)}")
    print(f"{'─'*55}\n")

    results = engine.repair_all(src)

    ok      = [r for r in results if r.success]
    failed  = [r for r in results if not r.success]
    no_issues = [r for r in ok if not r.issues]

    print(f"\n{'─'*55}")
    print(f"  RESUMEN")
    print(f"{'─'*55}")
    print(f"  Archivos procesados : {len(results):>5}")
    print(f"  Sin problemas       : {len(no_issues):>5}")
    print(f"  Reparados con éxito : {len(ok) - len(no_issues):>5}")
    print(f"  No reparables       : {len(failed):>5}")
    print(f"{'─'*55}")

    if failed:
        print("\n  Archivos no reparables:")
        for r in failed:
            print(f"    • {r.src.name}: {r.error}")

    print(f"\n  Archivos guardados en: {dst}\n")


if __name__ == "__main__":
    main()
