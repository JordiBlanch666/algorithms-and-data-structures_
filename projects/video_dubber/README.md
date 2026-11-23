# Video Dubber → Latin American Spanish

An automatic dubbing tool that downloads videos from **YouTube** or **VK** and creates a version dubbed into **Latin American Spanish** using AI. The source language is detected automatically — it works with Russian, English, French, German and any other language Whisper supports.

The result sounds like a **documentary voice-over**: the dubbed voice plays at natural speed while the original audio (music, ambience) stays in the background at low volume.

## Pipeline

```
Video URL (YouTube or VK) — or a local file
    │
    ├─ youtube.com / youtu.be ──► yt-dlp Android client (no cookies)
    └─ vk.com / vkvideo.ru ─────► no cookies → Edge cookies → Chrome → Firefox
    │
    ▼
Audio extraction to 16 kHz mono WAV (ffmpeg)
    │
    ▼
Transcription + language detection (faster-whisper)
    │
    ▼
Translation X → ES (Google Translate)
    │
    ▼
Latin American Spanish speech synthesis (Edge TTS)
    │
    ▼
Documentary-style assembly — voice at natural speed (pydub + ffmpeg)
    │
    ▼
Mix: dubbed voice (100%) + original background audio (15%) (ffmpeg)
    │
    ▼
Dubbed video (.mp4)
```

## Prerequisites

- **Python 3.10+**
- **ffmpeg** (must be on the system PATH)

### Installing ffmpeg on Windows

1. Download the *release full* build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the ZIP into a folder (e.g. `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to the environment variables → PATH

Check that it works:

```bash
ffmpeg -version
```

## Installation

```bash
cd projects/video_dubber
pip install -r requirements.txt
```

## Quick start — dubber.bat

Double-click `dubber.bat`. The interactive wizard asks step by step for:

1. The video URL (YouTube or VK) or a path to a local file
2. The source language (Enter = auto-detect)
3. The Latin American voice (menu 1–4)
4. The Whisper model (transcription quality)
5. The background audio volume (0–100%)

> **Private or group VK videos:** if the script can't download the video, fully close Edge or Chrome and try again. Windows locks the cookie file while the browser is open.

## Command-line usage

```bash
python dubber.py <URL> [options]
```

### Examples

```bash
# YouTube — auto-detect the language
python dubber.py https://youtu.be/XXXX

# VK — auto-detect the language
python dubber.py https://vk.com/video-XXXXXXX_XXXXXXX

# Force the source language
python dubber.py https://youtu.be/XXXX --source-lang en
python dubber.py https://vk.com/video-XXXX --source-lang ru

# Choose the output file
python dubber.py <URL> -o my_dubbed_video.mp4

# Better transcription quality
python dubber.py <URL> --model small

# Change the dubbing voice
python dubber.py <URL> --voice es-MX-DaliaNeural

# Adjust the background audio volume (0.0 = silent, 1.0 = full original)
python dubber.py <URL> --bg-volume 0.20

# Use a local file instead of a URL
python dubber.py path/to/video.mp4 --source-lang fr
```

The first run downloads the Whisper `base` model (~150 MB).

The output file is saved in the script's folder as `<name>_dubbed_es_YYYYMMDD_HHMMSS.mp4`, so earlier dubs of the same video are never overwritten.

## Options

| Argument | Description | Default |
|----------|-------------|---------|
| `url` | Video URL (YouTube or VK) or path to a local file | *(required)* |
| `-o`, `--output` | Output file path (`.mp4`) | `<name>_dubbed_es_<timestamp>.mp4` |
| `--model` | Whisper model for transcription | `base` |
| `--voice` | Edge TTS voice for the dub | `es-MX-JorgeNeural` |
| `--source-lang` | ISO 639-1 code of the original language (`ru`, `en`, `fr`…). Auto-detects by default. | auto |
| `--bg-volume` | Volume of the original audio mixed in the background (`0.0`–`1.0`) | `0.15` |

## Downloading VK videos

Public VK videos need no extra setup.

For private or group videos, the script automatically tries to read the cookies from Edge, Chrome and Firefox (in that order). If that fails:

1. **Fully close** Edge or Chrome before running the script
2. Try again — yt-dlp can then read the cookie file without the browser locking it

You can also export a `cookies.txt` file with the "Get cookies.txt LOCALLY" extension and place it next to `dubber.py`.

## Supported source languages

Any language Whisper recognizes. Common codes:

| Code | Language |
|------|----------|
| `ru` | Russian |
| `en` | English |
| `fr` | French |
| `de` | German |
| `zh` | Chinese |
| `ja` | Japanese |
| `pt` | Portuguese |
| `it` | Italian |

## Whisper models

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `tiny` | ~75 MB | Very fast | Basic |
| `base` | ~150 MB | Fast | Good *(default)* |
| `small` | ~500 MB | Moderate | Very good |
| `medium` | ~1.5 GB | Slow | Excellent |
| `large-v3` | ~3 GB | Very slow | Best |

## Available voices (Latin American Spanish)

| Voice | Variant | Gender |
|-------|---------|--------|
| `es-MX-JorgeNeural` | Mexico | Male *(default)* |
| `es-MX-DaliaNeural` | Mexico | Female |
| `es-US-AlonsoNeural` | USA | Male |
| `es-AR-TomasNeural` | Argentina | Male |

> The script automatically checks that the voice is available in Edge TTS and falls back to the next one on the list if it isn't.

## Dependencies

| Library | Minimum version | Purpose |
|---------|-----------------|---------|
| `yt-dlp` | 2024.1.1 | Downloads videos from YouTube and VK |
| `faster-whisper` | 1.0.0 | Transcription and automatic language detection |
| `deep-translator` | 1.11.4 | Translation into Spanish (Google Translate) |
| `edge-tts` | 6.1.9 | Latin American Spanish speech synthesis |
| `pydub` | 0.25.1 | Audio manipulation and assembly |
| `ffmpeg` | — | Video/audio processing (external) |
