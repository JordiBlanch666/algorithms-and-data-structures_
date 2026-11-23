#!/usr/bin/env python3
"""
Video Dubber: any language → Latin American Spanish
Downloads a video from YouTube or VK and creates a version dubbed into
Latin American Spanish using AI. The source language is detected automatically.

Platforms:
  - YouTube: uses yt-dlp's Android client to avoid the anti-bot block
  - VK:      tries without cookies first; if that fails, uses browser cookies

Pipeline:
  1. Download the video (yt-dlp)
  2. Extract the audio as 16 kHz mono WAV (the format Whisper expects)
  3. Transcribe with faster-whisper → list of segments with timestamps
  4. Translate each segment into Spanish with Google Translate (deep-translator)
  5. Generate TTS audio for each segment with Microsoft Edge TTS (Latin American voice)
  6. Assemble the dubbed track at natural speed over a silent base (documentary style)
  7. Mix the dubbed track with the original audio at low volume (background music/ambience)
  8. Combine the original video + mixed track into a new mp4 (without re-encoding the video)

Usage:
    python dubber.py <YouTube_URL>
    python dubber.py <VK_URL>
    python dubber.py <URL> -o dubbed_video.mp4
    python dubber.py <URL> --model small --voice es-MX-JorgeNeural
    python dubber.py <URL> --source-lang ru
    python dubber.py <URL> --bg-volume 0.20
    python dubber.py path/to/video.mp4
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import argparse
from datetime import datetime
from pathlib import Path

# Force UTF-8 so emojis and special characters display correctly on Windows
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8')


# ─────────────────────────────────────────────
# Console helpers
# ─────────────────────────────────────────────

def step(msg: str):
    print(f"\n[→] {msg}...")

def ok(msg: str = "Done"):
    print(f"    ✓ {msg}")

def error(msg: str):
    print(f"\n[✗] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def check_ffmpeg():
    # ffmpeg: extract audio, adjust speed (atempo) and mix tracks
    # ffprobe: read the video's metadata and duration
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        error(
            "ffmpeg is not installed or not on the PATH.\n"
            "  Download it from: https://ffmpeg.org/download.html\n"
            "  On Windows: https://www.gyan.dev/ffmpeg/builds/"
        )

def run_ffmpeg(args: list, desc: str = "ffmpeg"):
    # Run ffmpeg and show the full stderr on failure instead of a generic error
    result = subprocess.run(['ffmpeg'] + args, capture_output=True, text=True)
    if result.returncode != 0:
        error(f"{desc} failed:\n{result.stderr.strip()}")

def get_video_duration(path: str) -> float:
    # Read the container's duration (more reliable than a single stream's)
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        error(f"ffprobe could not read the video:\n{result.stderr.strip()}")
    return float(json.loads(result.stdout)['format']['duration'])

def build_atempo_filter(ratio: float) -> str:
    # ffmpeg limits each atempo filter to the 0.5–2.0 range, so several are
    # chained when the ratio falls outside it (e.g. ratio=3.0 → atempo=2.0,atempo=1.5)
    filters = []
    while ratio > 2.0:
        filters.append("atempo=2.0")
        ratio /= 2.0
    while ratio < 0.5:
        filters.append("atempo=0.5")
        ratio /= 0.5
    filters.append(f"atempo={ratio:.6f}")
    return ",".join(filters)


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────

class _YtdlpLogger:
    # Hide progress and debug noise; only show real warnings and errors
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): print(f"    ⚠ {msg}", file=sys.stderr)
    def error(self, msg): print(f"    ✗ {msg}", file=sys.stderr)


def _ydlp_progress(d: dict):
    # Progress hook: shows percentage, speed and ETA on a single updating line
    if d['status'] == 'downloading':
        pct = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        print(f"\r    {pct:<7}  {speed:<14}  ETA: {eta:<6}", end='', flush=True)
    elif d['status'] == 'finished':
        size = (d.get('_total_bytes_str') or d.get('_downloaded_bytes_str') or '').strip()
        print(f"\r    100%    {size} downloaded{' ' * 20}")


def _base_ydl_opts(output_dir: str) -> dict:
    # Options shared by every downloader: mp4 format, no console spam
    return {
        'outtmpl': os.path.join(output_dir, 'original.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'logger': _YtdlpLogger(),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [_ydlp_progress],
    }


def _collect_download(output_dir: str) -> str | None:
    # Return the downloaded file's path, or None if it doesn't exist yet
    for f in Path(output_dir).glob('original.*'):
        return str(f)
    return None


def _download_youtube(url: str, output_dir: str) -> str:
    # Android client: avoids YouTube's anti-bot block without needing cookies
    try:
        import yt_dlp
    except ImportError:
        error("yt-dlp is not installed. Run: pip install yt-dlp")

    opts = _base_ydl_opts(output_dir)
    opts['extractor_args'] = {'youtube': {'player_client': ['android', 'web']}}

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        path = _collect_download(output_dir)
        if path:
            ok(f"Downloaded: {Path(path).name}")
            return path
    except Exception as e:
        error(
            f"Could not download the video.\n"
            f"  Error: {e}\n"
            f"\n"
            f"  Possible fixes:\n"
            f"  - Check that the URL is correct and the video is public\n"
            f"  - Update yt-dlp: pip install -U yt-dlp\n"
            f"  - Use a local file: python dubber.py path/to/video.mp4"
        )


def _download_vk(url: str, output_dir: str) -> str:
    # VK: try without cookies first (public videos), then with browser cookies.
    # IMPORTANT: the browser must be fully closed when using cookies,
    # otherwise Windows locks the SQLite file and copying it fails.
    try:
        import yt_dlp
    except ImportError:
        error("yt-dlp is not installed. Run: pip install yt-dlp")

    # vkvideo.ru is an alternative domain — yt-dlp extracts formats better from vk.com
    if 'vkvideo.ru' in url:
        url = url.replace('vkvideo.ru', 'vk.com')
        print(f"    Normalized URL: {url}")

    opts = _base_ydl_opts(output_dir)
    # Let VK warnings reach the logger and mimic a real browser
    opts.pop('no_warnings', None)
    opts['http_headers'] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://vk.com/',
    }

    def _clean():
        for f in Path(output_dir).glob('original.*'):
            f.unlink(missing_ok=True)

    # Attempt 1: no cookies (works for public VK videos)
    print("    → Attempt 1: no cookies...")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        path = _collect_download(output_dir)
        if path:
            ok(f"Downloaded: {Path(path).name}")
            return path
    except Exception as e:
        print(f"    ✗ No cookies: {e}", file=sys.stderr)
        _clean()

    # Attempt 2: a cookies.txt file in the script folder (more reliable than browser cookies)
    # To export it: use the "Get cookies.txt LOCALLY" extension in Chrome/Edge while signed in to vk.com
    cookies_file = Path(__file__).parent / 'cookies.txt'
    if cookies_file.exists():
        print("    → Trying cookies.txt...")
        try:
            file_opts = dict(opts)
            file_opts['cookiefile'] = str(cookies_file)
            with yt_dlp.YoutubeDL(file_opts) as ydl:
                ydl.download([url])
            path = _collect_download(output_dir)
            if path:
                ok(f"Downloaded with cookies.txt: {Path(path).name}")
                return path
        except Exception as e:
            print(f"    ✗ cookies.txt: {e}", file=sys.stderr)
            _clean()

    # Attempt 3: browser cookies
    # On Windows 11, Edge keeps running in the background after you close the window.
    # Ending the process releases the lock on the SQLite cookie file.
    print("    Ending background Edge/Chrome processes...")
    for exe in ['msedge.exe', 'chrome.exe']:
        subprocess.run(['taskkill', '/F', '/IM', exe], capture_output=True)
    time.sleep(1)

    last_exc = None
    for browser in ['edge', 'chrome', 'firefox']:
        print(f"    → Trying {browser} cookies...")
        try:
            browser_opts = dict(opts)
            browser_opts['cookiesfrombrowser'] = (browser,)
            with yt_dlp.YoutubeDL(browser_opts) as ydl:
                ydl.download([url])
            path = _collect_download(output_dir)
            if path:
                ok(f"Downloaded with {browser} cookies: {Path(path).name}")
                return path
        except Exception as e:
            last_exc = e
            print(f"    ✗ {browser}: {e}", file=sys.stderr)
            _clean()

    error(
        f"Could not download the VK video.\n"
        f"  Last error: {last_exc}\n"
        f"\n"
        f"  Most reliable fix:\n"
        f"  1. Install the 'Get cookies.txt LOCALLY' extension in Chrome or Edge\n"
        f"  2. Open vk.com while signed in\n"
        f"  3. Export the cookies and save the file as 'cookies.txt'\n"
        f"     in the same folder as dubber.bat\n"
        f"  4. Run it again\n"
        f"\n"
        f"  Alternatives:\n"
        f"  - Update yt-dlp: pip install -U yt-dlp\n"
        f"  - Check that the video is accessible with your VK account"
    )


def download_video(url: str, output_dir: str) -> str:
    # Route to the right downloader for the platform
    step(f"Downloading video from {url}")
    if 'vk.com' in url or 'vkvideo.ru' in url:
        return _download_vk(url, output_dir)
    return _download_youtube(url, output_dir)


def extract_audio(video_path: str, audio_path: str):
    step("Extracting audio")
    # 16 kHz mono PCM WAV: the exact format Whisper expects for best transcription
    run_ffmpeg([
        '-y', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        audio_path
    ], "Audio extraction")
    ok()


def transcribe(audio_path: str, model_size: str, language: str = None) -> tuple:
    label = f"'{language}'" if language else "auto-detected"
    step(f"Transcribing with Whisper '{model_size}' — language: {label} (the first run downloads the model)")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        error("faster-whisper is not installed. Run: pip install faster-whisper")

    # int8 on CPU: much faster than float32 with practically the same quality
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, language=language, beam_size=5)

    detected = info.language
    if not language:
        ok(f"Detected language: {detected} (probability: {info.language_probability:.0%})")

    # Keep only segments with real text; each one has start/end in seconds
    result = [
        {'start': seg.start, 'end': seg.end, 'text': seg.text.strip()}
        for seg in segments
        if seg.text.strip()
    ]
    ok(f"{len(result)} segments transcribed")
    return result, detected


def translate(segments: list, source_lang: str) -> list:
    step(f"Translating {source_lang} → Spanish (Google Translate)")
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        error("deep-translator is not installed. Run: pip install deep-translator")

    # Translate segment by segment to keep Whisper's timestamps
    translator = GoogleTranslator(source=source_lang, target='es')
    for seg in segments:
        seg['translated'] = translator.translate(seg['text']) if seg['text'] else ''

    ok(f"{len(segments)} segments translated")
    return segments


# Edge TTS voices that are guaranteed to be Latin American Spanish.
# Used as fallbacks, in order, if the chosen voice isn't available in the API.
VOICES_LATAM = [
    "es-MX-JorgeNeural",   # Mexico, male
    "es-MX-DaliaNeural",   # Mexico, female
    "es-US-AlonsoNeural",  # USA, male
    "es-AR-TomasNeural",   # Argentina, male
]


async def validate_voice(voice: str) -> str:
    # Ask the Edge TTS API which voices are available right now.
    # Stops a wrong name from silently failing on every segment.
    try:
        import edge_tts
        available = {v['ShortName'] for v in await edge_tts.list_voices()}
        if voice in available:
            return voice
        print(f"    ⚠ Voice '{voice}' is not available.", file=sys.stderr)
        for v in VOICES_LATAM:
            if v in available:
                print(f"    → Using fallback voice: {v}", file=sys.stderr)
                return v
    except Exception:
        pass
    return voice


async def _tts_save(text: str, path: str, voice: str, semaphore: asyncio.Semaphore):
    try:
        import edge_tts
    except ImportError:
        error("edge-tts is not installed. Run: pip install edge-tts")
    async with semaphore:
        # Up to 3 retries per segment to absorb transient network errors
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(path)
                return
            except Exception as e:
                if attempt == 2:
                    # Report the error instead of dropping it silently
                    print(f"    ⚠ Segment skipped (TTS failed: {e})", file=sys.stderr)
                    return
                await asyncio.sleep(1)


async def generate_all_tts(segments: list, tmp_dir: str, voice: str):
    voice = await validate_voice(voice)
    step(f"Generating speech with Edge TTS (voice: {voice})")
    # Semaphore of 10: limits simultaneous API requests to avoid throttling
    semaphore = asyncio.Semaphore(10)
    tasks = []
    for i, seg in enumerate(segments):
        text = seg.get('translated', '').strip()
        if text and len(text) > 1:
            path = os.path.join(tmp_dir, f'tts_{i}.mp3')
            tasks.append(_tts_save(text, path, voice, semaphore))
    # Every segment is generated in parallel (within the semaphore limit)
    await asyncio.gather(*tasks)
    ok(f"{len(tasks)} voice clips generated")


def build_dubbed_audio(segments: list, total_duration_s: float, tmp_dir: str) -> str:
    step("Assembling the audio track (documentary style)")
    try:
        from pydub import AudioSegment
    except ImportError:
        error("pydub is not installed. Run: pip install pydub")

    # Silent base as long as the original video
    total_ms = int(total_duration_s * 1000)
    dubbed = AudioSegment.silent(duration=total_ms, frame_rate=44100)

    for i, seg in enumerate(segments):
        tts_raw = os.path.join(tmp_dir, f'tts_{i}.mp3')
        if not os.path.exists(tts_raw):
            continue

        tts_audio = AudioSegment.from_mp3(tts_raw)
        if len(tts_audio) == 0:
            continue

        start_ms = int(seg['start'] * 1000)

        # Available gap = time until the next line starts (or the video ends).
        # It's the most this segment can take without covering the next line.
        if i + 1 < len(segments):
            next_start_ms = int(segments[i + 1]['start'] * 1000)
        else:
            next_start_ms = total_ms
        gap_ms = max(next_start_ms - start_ms, 1)  # avoid division by zero

        # Documentary style: the voice always plays at natural speed.
        # It's only compressed when the TTS runs longer than the whole gap.
        if len(tts_audio) > gap_ms and gap_ms > 200:
            ratio = len(tts_audio) / gap_ms
            tts_wav = os.path.join(tmp_dir, f'tts_{i}_raw.wav')
            tts_adj = os.path.join(tmp_dir, f'tts_{i}_adj.wav')
            tts_audio.export(tts_wav, format='wav')
            atempo = build_atempo_filter(ratio)
            run_ffmpeg([
                '-y', '-i', tts_wav, '-filter:a', atempo, tts_adj
            ], f"atempo segment {i}")
            tts_audio = AudioSegment.from_wav(tts_adj)

        # Overlay the TTS clip on the silent base at the right timestamp
        dubbed = dubbed.overlay(tts_audio, position=start_ms)

    out_wav = os.path.join(tmp_dir, 'dubbed.wav')
    dubbed.export(out_wav, format='wav')
    ok()
    return out_wav


def merge_video_audio(video_path: str, audio_path: str, output_path: str, bg_volume: float = 0.15):
    step(f"Combining the video with the dubbed track (original background at {int(bg_volume * 100)}%)")
    # Mix the lowered original audio (background ambience) with the full-volume TTS track.
    # normalize=0: stops amix from dividing each input's volume by the number of inputs.
    filter_complex = (
        f"[0:a]volume={bg_volume}[bg];"
        f"[bg][1:a]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    run_ffmpeg([
        '-y',
        '-i', video_path,
        '-i', audio_path,
        '-filter_complex', filter_complex,
        '-map', '0:v:0',
        '-map', '[aout]',
        '-c:v', 'copy',
        '-shortest',
        output_path
    ], "Video and audio mix")
    ok(f"Video saved: {output_path}")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def dub(url: str, output_path: str = None, model_size: str = "base",
        voice: str = "es-MX-JorgeNeural", source_lang: str = None,
        bg_volume: float = 0.15):
    # bg_volume: level of the original audio mixed in the background (0.0=silent, 1.0=full volume)
    check_ffmpeg()

    # Accept both URLs and local file paths
    is_local = os.path.isfile(url)

    # tempfile.TemporaryDirectory cleans up every intermediate file when it finishes
    with tempfile.TemporaryDirectory(prefix='dubber_') as tmp_dir:
        if is_local:
            step(f"Using local file: {url}")
            video_path = url
            ok()
        else:
            video_path = download_video(url, tmp_dir)

        if not output_path:
            base = Path(video_path).stem
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Timestamp in the name so earlier dubs of the same video aren't overwritten
            output_path = str(Path(__file__).parent / f"{base}_dubbed_es_{ts}.mp4")

        audio_wav = os.path.join(tmp_dir, 'audio.wav')
        extract_audio(video_path, audio_wav)

        total_duration = get_video_duration(video_path)

        segments, detected_lang = transcribe(audio_wav, model_size, language=source_lang)
        if not segments:
            error("No speech was detected in the video.")

        if detected_lang == 'es':
            error(
                "The video is already in Spanish. There's nothing to translate.\n"
                "  If the detected language is wrong, use --source-lang <code>"
            )

        segments = translate(segments, detected_lang)

        asyncio.run(generate_all_tts(segments, tmp_dir, voice))

        dubbed_wav = build_dubbed_audio(segments, total_duration, tmp_dir)

        merge_video_audio(video_path, dubbed_wav, output_path, bg_volume=bg_volume)

    print(f"\n{'='*50}")
    print(f"  Dubbing finished -> {output_path}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Dub videos into Latin American Spanish with AI (auto-detects the source language)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dubber.py https://youtu.be/XXXX
  python dubber.py https://vk.com/video-XXXXXXX_XXXXXXX
  python dubber.py <URL> -o my_video.mp4
  python dubber.py <URL> --model small
  python dubber.py <URL> --voice es-MX-DaliaNeural
  python dubber.py <URL> --source-lang ru
  python dubber.py <URL> --bg-volume 0.20
  python dubber.py path/to/video.mp4 --source-lang fr

Whisper models (better quality = slower):
  tiny | base | small | medium | large-v3

Available Latin American voices (Edge TTS):
  es-MX-JorgeNeural   (Mexico, male)  <- default
  es-MX-DaliaNeural   (Mexico, female)
  es-US-AlonsoNeural  (USA, male)
  es-AR-TomasNeural   (Argentina, male)

Common ISO 639-1 language codes:
  ru (Russian)  en (English)  fr (French)  de (German)
  zh (Chinese)  ja (Japanese)  pt (Portuguese)  it (Italian)
        """
    )
    parser.add_argument('url', help='Video URL or path to a local file')
    parser.add_argument('-o', '--output', help='Output file path (.mp4)')
    parser.add_argument(
        '--model', default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large-v3'],
        help='Whisper model to use (default: base)'
    )
    parser.add_argument(
        '--voice', default='es-MX-JorgeNeural',
        help='Edge TTS voice (default: es-MX-JorgeNeural)'
    )
    parser.add_argument(
        '--source-lang', default=None, dest='source_lang',
        metavar='CODE',
        help='ISO 639-1 code of the original language (e.g. ru, en, fr). Default: auto-detect'
    )
    parser.add_argument(
        '--bg-volume', default=0.15, type=float, dest='bg_volume',
        metavar='LEVEL',
        help='Volume of the original background audio (0.0=silent, 0.15=15%% default, 1.0=full)'
    )

    args = parser.parse_args()
    dub(args.url, args.output, args.model, args.voice,
        source_lang=args.source_lang, bg_volume=args.bg_volume)


if __name__ == '__main__':
    main()
