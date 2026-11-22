"""Reads metadata (title, artist, duration and cover art) from audio files."""
from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path

from mutagen import File as MutagenFile

@dataclass
class Track:
    path: Path
    title: str
    artist: str
    duration: float
    cover: bytes | None = None


def read_track(path: Path) -> Track:
    title = path.stem
    artist = "Unknown artist"
    if " - " in title:
        artist, title = (part.strip() for part in title.split(" - ", 1))

    duration = 0.0
    cover = None
    audio = MutagenFile(path, easy=path.suffix.lower() not in (".m4a", ".m4p"))
    if audio:
        if audio.info:
            duration = float(audio.info.length)
        if audio.tags:
            if path.suffix.lower() in (".m4a", ".m4p"):
                title = str(audio.tags.get("\xa9nam", [title])[0])
                artist = str(audio.tags.get("\xa9ART", [artist])[0])
                covers = audio.tags.get("covr", [])
                if covers:
                    cover = bytes(covers[0])
            else:
                title = str(audio.tags.get("title", [title])[0])
                artist = str(audio.tags.get("artist", [artist])[0])
    if duration == 0 and path.suffix.lower() == ".wav":
        with wave.open(str(path), "rb") as wav_file:
            if wav_file.getframerate():
                duration = wav_file.getnframes() / wav_file.getframerate()
    return Track(path, title, artist, duration, cover)


def format_time(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 60}:{total % 60:02d}"
