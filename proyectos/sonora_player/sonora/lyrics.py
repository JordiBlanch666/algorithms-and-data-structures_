"""Lyrics: LRC file parsing and lookups in the public LRCLIB API."""
from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LRCLIB_URL = "https://lrclib.net/api/get"
NOT_FOUND = "No lyrics found for this song."
TIMESTAMP = re.compile(r"\[(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?\]")


def parse_lrc_entries(text: str) -> list[tuple[float, str]]:
    """Convert LRC text into a sorted list of (second, line)."""
    entries = []
    for line in text.splitlines():
        timestamps = TIMESTAMP.findall(line)
        lyric = TIMESTAMP.sub("", line).strip()
        if not lyric:
            continue
        for minutes, seconds, fraction in timestamps:
            fraction_seconds = float(f"0.{fraction}") if fraction else 0.0
            entries.append((int(minutes) * 60 + int(seconds) + fraction_seconds, lyric))
    return sorted(entries, key=lambda entry: entry[0])


def parse_lrc(text: str) -> str:
    """Return only the lyric text, without timestamps."""
    entries = parse_lrc_entries(text)
    if entries:
        return "\n\n".join(line for _, line in entries)
    return "\n\n".join(line.strip() for line in text.splitlines() if line.strip())


def fetch_lrclib(title: str, artist: str, timeout: float = 10) -> str:
    """Look up lyrics on LRCLIB, preferring the synced (LRC) version.

    Always returns text that can be shown to the user, even when the request fails.
    """
    params = urlencode({"track_name": title, "artist_name": artist})
    request = Request(f"{LRCLIB_URL}?{params}", headers={"User-Agent": "SonoraPlayer/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("syncedLyrics") or data.get("plainLyrics") or NOT_FOUND
    except HTTPError as error:
        if error.code == 404:
            return NOT_FOUND
        return f"LRCLIB returned an error ({error.code})."
    except URLError as error:
        return f"Couldn't connect to LRCLIB.\n\n{error}"
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as error:
        return f"Couldn't load the lyrics.\n\n{error}"
