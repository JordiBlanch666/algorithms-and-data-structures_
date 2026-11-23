# 🎵 Sonora — Desktop Music Player

A desktop audio player built with **Python + Tkinter**, featuring playlists, search, an animated
visualizer and **synced lyrics** that highlight line by line as the song plays.

## ✨ Features

- **Formats:** MP3, WAV, OGG, FLAC, AIFF and **M4A/AAC** (iTunes purchases)
- **Playlist:** add songs or entire folders, remove tracks, open and save **M3U** playlists
- **Search** by title or artist
- **Controls:** play/pause, previous/next, seek bar, volume and mute
- **Shuffle** without repeating songs, and **repeat** (one song or the whole list)
- **Album art** read from the file's metadata
- **Synced lyrics:** uses a `.lrc` file next to the song or fetches them from [LRCLIB](https://lrclib.net)
- Detects **`.m4p`** files (Apple DRM-protected) and explains why they can't be played

## 🗂️ Project structure

```
sonora_player/
├── main.py              # entry point
├── requirements.txt
├── sonora/
│   ├── player.py        # GUI and playback logic
│   ├── audio.py         # AAC/M4A decoding to WAV with PyAV
│   ├── metadata.py      # title, artist, duration and cover art (mutagen)
│   ├── lyrics.py        # LRC parsing and LRCLIB requests
│   └── theme.py         # colors and supported formats
└── tests/
    └── test_sonora.py   # 10 unit tests for the logic (no window needed)
```

I separated the UI from the logic so the important parts (lyrics, metadata and audio decoding)
can be tested without opening the window.

## ⚙️ How it works

| Part | How I solved it |
|---|---|
| Playback | `pygame-ce` (SDL_mixer) for MP3, WAV, OGG, FLAC and AIFF |
| AAC / M4A | SDL_mixer can't play AAC, so it's decoded with **PyAV** into a temporary WAV that is deleted when the track changes |
| Synced lyrics | LRC timestamps `[mm:ss.xx]` are converted to seconds, and a **binary search** (`bisect`) finds the line to highlight |
| Network calls without freezing the UI | The LRCLIB request runs in a **background thread** and returns the result through `root.after()` |
| Error handling | No internet, corrupted files or unsupported formats show a clear message instead of crashing |

## ▶️ How to run it

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt
python main.py
python -m unittest discover tests   # run the tests
```

## 👤 Author

**Jordi Blanch** — Software Engineering student (Hybridge)
