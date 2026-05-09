"""
MediaRecover — Recuperador de imágenes y vídeos eliminados para Windows
=======================================================================

Requiere:
  - Python 3.11+
  - Ejecutar como Administrador (acceso a sectores crudos del disco)
  - Sin dependencias externas (solo librería estándar)

Uso:
  python main.py --disk C: --output C:\\Recuperados
  python main.py --disk PhysicalDrive0 --output D:\\Recuperados --only-images
  python main.py --disk C: --output D:\\Recuperados --only-carving
  python main.py --list-disks
"""

import argparse
import ctypes
import logging
import sys
import time
from pathlib import Path

from disk_reader import list_physical_drives, list_logical_volumes
from recovery_engine import RecoveryEngine, RecoveryOptions


# ── Logger ────────────────────────────────────────────────────────────────────
def _setup_logging(verbose: bool):
    level  = logging.DEBUG if verbose else logging.INFO
    fmt    = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%H:%M:%S"
    logging.basicConfig(level=level, format=fmt, datefmt=datefmt,
                        stream=sys.stdout)


# ── Verificación de privilegios ───────────────────────────────────────────────
def _check_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# ── Barra de progreso ─────────────────────────────────────────────────────────
class ProgressBar:
    def __init__(self, width: int = 50):
        self.width  = width
        self._last  = ""

    def update(self, msg: str, current: int, total: int):
        if total > 0:
            pct  = current / total
            done = int(self.width * pct)
            bar  = "█" * done + "░" * (self.width - done)
            line = f"\r[{bar}] {pct:5.1%}  {msg[:40]:<40}"
        else:
            line = f"\r  ↳ {msg[:70]:<70}"

        if line != self._last:
            print(line, end="", flush=True)
            self._last = line

    def finish(self):
        print()  # nueva línea al terminar


# ── CLI ───────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mediarecover",
        description="Recuperador profundo de imágenes y vídeos eliminados (Windows)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --list-disks
  python main.py --disk C: --output D:\\Recuperados
  python main.py --disk PhysicalDrive0 --output D:\\Recuperados --only-images
  python main.py --disk C: --output D:\\Recuperados --only-carving --verbose
""",
    )

    p.add_argument("--list-disks", action="store_true",
                   help="Listar discos y volúmenes disponibles y salir")

    p.add_argument("--disk", metavar="DISCO",
                   help=r"Volumen (C:, D:) o disco físico (PhysicalDrive0)")
    p.add_argument("--output", metavar="DIRECTORIO",
                   help="Directorio de salida para archivos recuperados")

    # Filtros de tipo
    grp_type = p.add_mutually_exclusive_group()
    grp_type.add_argument("--only-images", action="store_true",
                          help="Recuperar solo imágenes")
    grp_type.add_argument("--only-videos", action="store_true",
                          help="Recuperar solo vídeos")

    # Métodos de recuperación
    grp_method = p.add_mutually_exclusive_group()
    grp_method.add_argument("--only-mft", action="store_true",
                             help="Usar solo análisis MFT (más rápido, requiere NTFS)")
    grp_method.add_argument("--only-carving", action="store_true",
                             help="Usar solo file carving (más lento, funciona en cualquier FS)")

    # Opciones de tamaño
    p.add_argument("--min-size", type=int, default=10_000, metavar="BYTES",
                   help="Tamaño mínimo del archivo a recuperar (por defecto: 10 000 bytes)")
    p.add_argument("--max-size", type=int, default=100 * 1024**3, metavar="BYTES",
                   help="Tamaño máximo del archivo a recuperar")

    p.add_argument("--no-deduplicate", action="store_true",
                   help="No eliminar duplicados (pueden generarse muchos archivos)")
    p.add_argument("--overwrite", action="store_true",
                   help="Sobreescribir archivos ya existentes en el directorio de salida")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Mostrar log detallado")

    return p


def _resolve_disk_path(disk: str) -> str:
    """Normaliza la entrada del usuario a una ruta Win32 válida."""
    disk = disk.strip()
    if disk.startswith(r"\\"):
        return disk
    if disk.upper().startswith("PHYSICALDRIVE"):
        return f"\\\\.\\{disk}"
    # Letra de unidad
    letter = disk.rstrip(":/\\").upper()
    return f"\\\\.\\{letter}:"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = _build_parser()
    args   = parser.parse_args()

    _setup_logging(args.verbose)
    log = logging.getLogger(__name__)

    # ── Listar discos ────────────────────────────────────────────────────────
    if args.list_disks:
        print("\n=== Discos físicos ===")
        for d in list_physical_drives():
            print(f"  {d}")
        print("\n=== Volúmenes lógicos ===")
        for v in list_logical_volumes():
            print(f"  {v}")
        print()
        return

    # ── Validaciones ─────────────────────────────────────────────────────────
    if not args.disk or not args.output:
        parser.error("Se requieren --disk y --output (o usa --list-disks)")

    if not _check_admin():
        print(
            "\n⚠  ADVERTENCIA: No se detectan privilegios de Administrador.\n"
            "   El acceso a sectores crudos del disco puede fallar.\n"
            "   Ejecuta este script como Administrador para mejores resultados.\n"
        )

    disk_path  = _resolve_disk_path(args.disk)
    output_dir = Path(args.output)

    images = not args.only_videos
    videos = not args.only_images

    use_mft     = not args.only_carving
    use_carving = not args.only_mft

    # ── Configurar progreso ───────────────────────────────────────────────────
    pb = ProgressBar()

    def progress(msg: str, current: int, total: int):
        pb.update(msg, current, total)

    opts = RecoveryOptions(
        disk_path    = disk_path,
        output_dir   = output_dir,
        images       = images,
        videos       = videos,
        use_mft      = use_mft,
        use_carving  = use_carving,
        min_size     = args.min_size,
        max_size     = args.max_size,
        deduplicate  = not args.no_deduplicate,
        overwrite    = args.overwrite,
        progress_cb  = progress,
    )

    print(f"\n{'─'*60}")
    print(f"  MediaRecover — Recuperación de imágenes y vídeos")
    print(f"{'─'*60}")
    print(f"  Disco   : {disk_path}")
    print(f"  Salida  : {output_dir}")
    print(f"  Tipos   : {'imágenes ' if images else ''}{'vídeos' if videos else ''}")
    print(f"  Métodos : {'MFT ' if use_mft else ''}{'carving' if use_carving else ''}")
    print(f"{'─'*60}\n")

    t0 = time.time()
    try:
        engine = RecoveryEngine(opts)
        stats  = engine.run()
    except PermissionError as e:
        pb.finish()
        print(f"\n✗ Error de permisos: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        pb.finish()
        print("\n⚠  Recuperación interrumpida por el usuario.")
        sys.exit(0)
    finally:
        pb.finish()

    elapsed = time.time() - t0
    print(f"\n{'─'*60}")
    print(f"  RESUMEN DE RECUPERACIÓN")
    print(f"{'─'*60}")
    print(f"  Encontrados por MFT    : {stats.mft_found:>8,}")
    print(f"  Encontrados por carving: {stats.carved_found:>8,}")
    print(f"  Archivos guardados     : {stats.saved:>8,}")
    print(f"  Omitidos (dupl./tamaño): {stats.skipped:>8,}")
    print(f"  Errores de lectura     : {stats.errors:>8,}")
    print(f"  Tiempo total           : {elapsed:>8.1f} s")
    print(f"{'─'*60}")
    print(f"  Archivos en: {output_dir}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
