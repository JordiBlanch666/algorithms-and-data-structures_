# Author: Jordi Y Blanch
"""
Finds which sectors of the physical disk hold specific folders.
Uses FSCTL_GET_RETRIEVAL_POINTERS to get the real clusters of each path.
That way carving only scans the relevant areas instead of the whole disk.
"""
import ctypes
import ctypes.wintypes as wt
import struct
import os
import logging
from pathlib import Path

log = logging.getLogger(__name__)

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.restype  = ctypes.c_void_p
kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
kernel32.DeviceIoControl.argtypes = [
    ctypes.c_void_p, wt.DWORD,
    ctypes.c_void_p, wt.DWORD,
    ctypes.c_void_p, wt.DWORD,
    ctypes.POINTER(wt.DWORD), ctypes.c_void_p,
]

GENERIC_READ           = 0x80000000
FILE_SHARE_READ        = 0x00000001
FILE_SHARE_WRITE       = 0x00000002
OPEN_EXISTING          = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000   # needed to open directories
FSCTL_GET_RETRIEVAL_POINTERS = 0x00090073
INVALID_HANDLE_VALUE   = ctypes.c_void_p(-1).value

# Scan margin around each cluster found (in clusters)
SCAN_MARGIN_CLUSTERS = 50_000   # ~200 MB with 4 KB clusters


def _get_cluster_size(volume: str) -> int:
    """Get the volume's cluster size (e.g. 'C:\\')."""
    spc  = wt.DWORD(0)
    bps  = wt.DWORD(0)
    fc   = wt.DWORD(0)
    tc   = wt.DWORD(0)
    ok = kernel32.GetDiskFreeSpaceW(volume, ctypes.byref(spc),
                                     ctypes.byref(bps), ctypes.byref(fc),
                                     ctypes.byref(tc))
    if ok:
        return spc.value * bps.value
    return 4096


def _get_retrieval_pointers(path: str) -> list[tuple[int, int]]:
    """
    Return the extents (start_lcn, num_clusters) of a file or folder.
    Empty if it can't be opened or the path doesn't exist.
    """
    h = kernel32.CreateFileW(
        path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if h == INVALID_HANDLE_VALUE:
        return []

    try:
        # Input: StartingVcn = 0
        input_buf  = struct.pack("<q", 0)
        output_buf = ctypes.create_string_buffer(65536)
        bytes_ret  = wt.DWORD(0)

        ok = kernel32.DeviceIoControl(
            h,
            FSCTL_GET_RETRIEVAL_POINTERS,
            input_buf, len(input_buf),
            output_buf, len(output_buf),
            ctypes.byref(bytes_ret),
            None,
        )

        if not ok and ctypes.get_last_error() != 234:  # 234 = MORE_DATA (aceptable)
            return []

        raw = output_buf.raw[:bytes_ret.value]
        if len(raw) < 16:
            return []

        extent_count = struct.unpack_from("<I", raw, 0)[0]
        # starting_vcn = struct.unpack_from("<q", raw, 8)[0]  # not needed

        extents = []
        pos = 16
        prev_vcn = 0
        for _ in range(extent_count):
            if pos + 16 > len(raw):
                break
            next_vcn = struct.unpack_from("<q", raw, pos)[0]
            lcn      = struct.unpack_from("<q", raw, pos + 8)[0]
            num_clusters = next_vcn - prev_vcn
            if lcn >= 0:   # lcn = -1 means sparse/unallocated
                extents.append((lcn, num_clusters))
            prev_vcn = next_vcn
            pos += 16

        return extents

    finally:
        kernel32.CloseHandle(h)


def get_scan_ranges(
    paths: list[str],
    volume_letter: str,
    sector_size: int = 512,
    cluster_size: int | None = None,
) -> list[tuple[int, int]]:
    """
    For each path, get its clusters and return the sector ranges to scan
    (with a margin). Overlapping ranges are merged.

    Returns a list of (start_sector, end_sector).
    """
    cs = cluster_size or _get_cluster_size(volume_letter + "\\")
    sectors_per_cluster = cs // sector_size

    raw_ranges: list[tuple[int, int]] = []

    for path in paths:
        if not os.path.exists(path):
            log.debug(f"Path does not exist, skipped: {path}")
            continue

        extents = _get_retrieval_pointers(path)
        if not extents:
            log.debug(f"No extents found for: {path}")
            continue

        log.info(f"  {path}: {len(extents)} extent(s)")
        for lcn, num_clusters in extents:
            start_cluster = max(0, lcn - SCAN_MARGIN_CLUSTERS)
            end_cluster   = lcn + num_clusters + SCAN_MARGIN_CLUSTERS
            start_sector  = start_cluster * sectors_per_cluster
            end_sector    = end_cluster   * sectors_per_cluster
            raw_ranges.append((start_sector, end_sector))
            log.info(f"    LCN {lcn} + {num_clusters} clusters → "
                     f"sectores {start_sector:,} – {end_sector:,}")

    if not raw_ranges:
        return []

    # Merge overlapping ranges
    raw_ranges.sort()
    merged: list[tuple[int, int]] = [raw_ranges[0]]
    for start, end in raw_ranges[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    total_sectors = sum(e - s for s, e in merged)
    log.info(f"Merged ranges: {len(merged)}, total {total_sectors:,} sectores "
             f"({total_sectors * sector_size / (1024**3):.2f} GB)")
    return merged


def build_hint_paths(username: str, extra_paths: list[str] | None = None) -> list[str]:
    """
    Build the list of relevant paths to search for deleted videos:
    - The user's Videos folder
    - The Recycle Bin
    - Temporary folders
    - Optional extra paths
    """
    paths = [
        f"C:\\Users\\{username}\\Videos",
        f"C:\\Users\\{username}\\Downloads",
        f"C:\\Users\\{username}\\Desktop",
        f"C:\\$Recycle.Bin",
        f"C:\\Windows\\Temp",
        f"C:\\Users\\{username}\\AppData\\Local\\Temp",
    ]
    if extra_paths:
        paths.extend(extra_paths)
    return paths
