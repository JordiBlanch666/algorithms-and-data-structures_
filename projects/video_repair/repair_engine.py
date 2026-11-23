# Author: Jordi Y Blanch
"""
Main engine of the video repairer.
Detects the format and hands off to the matching module.
"""
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from mp4_repair import repair_mp4
from avi_repair import repair_avi
from mkv_repair import repair_mkv
from mpg_repair import repair_mpg
from utils import human_size, backup_file

log = logging.getLogger(__name__)

SUPPORTED = {
    ".mp4":  repair_mp4,
    ".m4v":  repair_mp4,
    ".mov":  repair_mp4,
    ".avi":  repair_avi,
    ".mkv":  repair_mkv,
    ".webm": repair_mkv,
    ".mpg":  repair_mpg,
    ".mpeg": repair_mpg,
    ".vob":  repair_mpg,
}


@dataclass
class RepairResult:
    src: Path
    dst: Path
    format: str
    issues: list[str]
    fixes: list[str]
    success: bool
    output_size: int
    error: str = ""

    def summary(self) -> str:
        if self.success:
            return (f"✓ {self.src.name} → {self.dst.name} "
                    f"({human_size(self.output_size)}) "
                    f"fixes={self.fixes}")
        return f"✗ {self.src.name}: {self.error or 'unknown failure'}"


class RepairEngine:
    """
    Repairs one or more corrupted video files.

    Basic usage:
        engine = RepairEngine(output_dir=Path("repaired"))
        for result in engine.repair_all(Path("corrupted")):
            print(result.summary())
    """

    def __init__(self, output_dir: Path, backup: bool = True, overwrite: bool = False):
        self.output_dir = output_dir
        self.backup     = backup
        self.overwrite  = overwrite
        output_dir.mkdir(parents=True, exist_ok=True)

    def repair_file(self, src: Path) -> RepairResult:
        ext = src.suffix.lower()
        if ext not in SUPPORTED:
            return RepairResult(
                src=src, dst=src, format=ext,
                issues=["unsupported_format"], fixes=[],
                success=False, output_size=0,
                error=f"Format {ext} is not supported. Valid: {list(SUPPORTED)}",
            )

        dst = self._dest_path(src)
        if self.backup and src != dst:
            backup_file(src)

        repairer = SUPPORTED[ext]
        log.info(f"Repairing: {src.name} ({human_size(src.stat().st_size)})")

        try:
            result_dict = repairer(src, dst)
        except Exception as e:
            log.error(f"Unexpected error repairing {src.name}: {e}")
            return RepairResult(
                src=src, dst=dst, format=ext,
                issues=["unexpected_error"], fixes=[],
                success=False, output_size=0, error=str(e),
            )

        return RepairResult(
            src=src, dst=dst, format=ext,
            issues=result_dict.get("issues", []),
            fixes=result_dict.get("fixes", []),
            success=result_dict.get("success", False),
            output_size=result_dict.get("output_size", 0),
            error=result_dict.get("error", ""),
        )

    def repair_all(self, source: Path) -> list[RepairResult]:
        """
        Repair every video file in `source` (a file or a folder).
        """
        if source.is_file():
            files = [source]
        else:
            files = [f for f in source.rglob("*") if f.suffix.lower() in SUPPORTED]

        results = []
        for f in sorted(files):
            result = self.repair_file(f)
            results.append(result)
            log.info(result.summary())

        return results

    def _dest_path(self, src: Path) -> Path:
        dst = self.output_dir / src.name
        if not self.overwrite and dst.exists():
            stem, suffix = src.stem, src.suffix
            i = 1
            while dst.exists():
                dst = self.output_dir / f"{stem}_repaired_{i}{suffix}"
                i += 1
        return dst
