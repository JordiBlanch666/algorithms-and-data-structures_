# MediaRecover — Deep Recovery of Deleted Images and Videos

> **Author:** Jordi Y Blanch

A forensic recovery tool written in pure Python (no external dependencies).
It works directly on the disk's raw sectors through the Win32 API.

## How it works

### Method 1 — MFT analysis (NTFS)
Reads the **Master File Table** of the NTFS file system to find entries for
files marked as deleted. If their data runs (data clusters) haven't been
overwritten yet, it rebuilds the complete file.

```
Disk → Boot Sector → MFT offset → FILE entries → Data Runs → File
```

### Method 2 — File carving
Scans **every sector of the disk** for known signatures (magic bytes),
completely independent of the file system. It works even on formatted
disks or disks with a damaged MFT.

```
Disk → Raw sectors → Magic bytes → Size estimate → File
```

## Supported formats

### Images
| Extension | Description |
|-----------|-------------|
| JPG/JPEG  | JPEG / JFIF / EXIF |
| PNG       | Portable Network Graphics |
| GIF       | GIF87a / GIF89a |
| BMP       | Windows Bitmap |
| TIF/TIFF  | Tagged Image File Format |
| WebP      | Google WebP |
| HEIC/HEIF | Apple HEIC (iPhone) |
| CR2/CR3   | Canon RAW |
| NEF       | Nikon RAW |
| ARW       | Sony RAW |
| DNG       | Adobe DNG |
| ORF       | Olympus RAW |
| RW2       | Panasonic RAW |

### Videos
| Extension | Description |
|-----------|-------------|
| MP4       | MPEG-4 (several variants) |
| MOV       | Apple QuickTime |
| AVI       | Audio Video Interleave |
| MKV       | Matroska / WebM |
| WMV       | Windows Media Video |
| FLV       | Flash Video |
| MPG/MPEG  | MPEG-1/2 |
| 3GP       | Mobile video |
| MTS/M2TS  | AVCHD (Sony/Panasonic cameras) |
| VOB       | DVD Video Object |

## Requirements

- Python 3.11+
- Windows (uses the Win32 API directly)
- **Run as Administrator** (needed to read raw sectors)

## Installation

No external libraries to install.

```bash
git clone https://github.com/JordiBlanch666/algorithms-and-data-structures_.git
cd algorithms-and-data-structures_/projects/file_recovery
```

## Usage

### List the available disks
```bash
python main.py --list-disks
```

### Recover everything from drive C:
```bash
python main.py --disk C: --output D:\Recovered
```

### Images only, file carving only (deeper)
```bash
python main.py --disk C: --output D:\Recovered --only-images --only-carving
```

### Whole physical disk (includes unpartitioned space)
```bash
python main.py --disk PhysicalDrive0 --output D:\Recovered
```

### Large videos only (at least 10 MB)
```bash
python main.py --disk C: --output D:\Recovered --only-videos --min-size 10000000
```

### Focus the scan on a user's folders (much faster)
```bash
python main.py --disk C: --output D:\Recovered --hint-user YourUser
```

### Check which recovered videos can play
```bash
python verify.py D:\Recovered --viable-only
```

## Project structure

```
file_recovery/
├── main.py             # CLI and entry point
├── disk_reader.py      # Low-level disk access (Win32 API)
├── mft_parser.py       # NTFS Master File Table parser
├── file_carver.py      # Raw-sector signature scanner
├── signatures.py       # Magic-byte database (images + videos)
├── cluster_locator.py  # Maps folders to disk sectors to narrow the scan
├── recovery_engine.py  # Orchestrator: coordinates both methods
├── verify.py           # Checks whether recovered videos are playable
└── README.md
```

## Output structure

```
D:\Recovered\
├── mft\
│   ├── images\     ← files recovered from the MFT
│   └── videos\
└── carving\
    ├── images\     ← files recovered by carving
    ├── videos\
    └── raw\
```

## Important notes

- **Act fast**: the longer it's been since the deletion, the more likely it is
  that the sectors have been overwritten.
- **Don't write to the disk you're recovering from**: install Python and run the
  script from another disk or a live USB.
- Carving can produce **false positives** (corrupted or partial files).
  That's normal; review the results with an image viewer.
- Camera RAW files (CR2, NEF, ARW) are similar to TIFF and may need
  Adobe Camera Raw or the camera's own software to open.
