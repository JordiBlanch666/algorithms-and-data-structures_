# VideoRepair — Corrupted Video Repairer

> **Author:** Jordi Y Blanch

A corrupted-video repair tool written in pure Python (no external dependencies).
It supports MP4, MOV, AVI, MKV, WebM, MPG and VOB.

## How it works

It analyzes the internal structure of the video container and fixes the most common problems:

- **MP4 / MOV**: rebuilds the `moov` atom, adjusts chunk offsets, inserts `ftyp` if it's missing
- **AVI**: rebuilds the `idx1` index by scanning the `movi` block, fixes the RIFF size
- **MKV / WebM**: rebuilds the `SeekHead`, marks the `Segment` size as unknown
- **MPG / MPEG**: drops corrupted packets, truncates trailing garbage

## Requirements

- Python 3.11+
- No external dependencies

## Usage

```bash
# Diagnose a file
python main_repair.py --diagnose video.mp4

# Repair a file
python main_repair.py --input video.mp4 --output C:\Repaired

# Repair a whole folder
python main_repair.py --input C:\Recovered --output C:\Repaired
```

## Structure

```
video_repair/
├── main_repair.py     — Main CLI
├── repair_engine.py   — Orchestrator
├── mp4_repair.py      — MP4 / MOV / M4V repairer
├── avi_repair.py      — AVI repairer
├── mkv_repair.py      — MKV / WebM repairer
├── mpg_repair.py      — MPG / MPEG / VOB repairer
└── utils.py           — Shared binary helpers
```
