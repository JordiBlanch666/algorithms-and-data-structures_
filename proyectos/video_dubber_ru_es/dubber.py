#!/usr/bin/env python3
"""
Video Dubber: Cualquier idioma → Español Latino
Descarga un video de YouTube o VK y genera una versión doblada al español
latinoamericano usando IA. El idioma de origen se detecta automáticamente.

Plataformas:
  - YouTube: usa cliente Android de yt-dlp para evitar bloqueo anti-bot
  - VK:      intenta sin cookies primero; si falla, usa cookies del navegador

Pipeline:
  1. Descarga el video (yt-dlp)
  2. Extrae el audio en WAV mono 16 kHz (formato que exige Whisper)
  3. Transcribe con faster-whisper → lista de segmentos con timestamps
  4. Traduce cada segmento al español con Google Translate (deep-translator)
  5. Genera audio TTS para cada segmento con Microsoft Edge TTS (voz latinoamericana)
  6. Ensambla la pista doblada a velocidad natural sobre una base silenciosa (estilo documental)
  7. Mezcla la pista doblada con el audio original a bajo volumen (música/ambiente de fondo)
  8. Combina video original + pista mezclada en un nuevo mp4 (sin recodificar video)

Uso:
    python dubber.py <URL_YouTube>
    python dubber.py <URL_VK>
    python dubber.py <URL> -o video_doblado.mp4
    python dubber.py <URL> --modelo small --voz es-MX-JorgeNeural
    python dubber.py <URL> --idioma-origen ru
    python dubber.py <URL> --volumen-fondo 0.20
    python dubber.py ruta/al/video.mp4
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import argparse
from datetime import datetime
from pathlib import Path

# Forzar UTF-8 para que emojis y caracteres especiales se muestren bien en Windows
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8')


# ─────────────────────────────────────────────
# Utilidades de consola
# ─────────────────────────────────────────────

def step(msg: str):
    print(f"\n[→] {msg}...")

def ok(msg: str = "Listo"):
    print(f"    ✓ {msg}")

def error(msg: str):
    print(f"\n[✗] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def check_ffmpeg():
    # ffmpeg: extraer audio, ajustar velocidad (atempo) y mezclar pistas
    # ffprobe: leer metadatos y duración del video
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        error(
            "ffmpeg no está instalado o no está en el PATH.\n"
            "  Descárgalo desde: https://ffmpeg.org/download.html\n"
            "  En Windows: https://www.gyan.dev/ffmpeg/builds/"
        )

def run_ffmpeg(args: list, desc: str = "ffmpeg"):
    # Ejecuta ffmpeg y muestra el stderr completo si falla, en lugar de error genérico
    result = subprocess.run(['ffmpeg'] + args, capture_output=True, text=True)
    if result.returncode != 0:
        error(f"{desc} falló:\n{result.stderr.strip()}")

def get_video_duration(path: str) -> float:
    # Lee la duración del contenedor (más fiable que la del stream individual)
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        error(f"ffprobe no pudo leer el video:\n{result.stderr.strip()}")
    return float(json.loads(result.stdout)['format']['duration'])

def build_atempo_filter(ratio: float) -> str:
    # ffmpeg limita cada filtro atempo al rango 0.5–2.0, así que se encadenan
    # varios si el ratio queda fuera (ej: ratio=3.0 → atempo=2.0,atempo=1.5)
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
    # Suprime el ruido de progreso y debug; muestra solo advertencias y errores reales
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): print(f"    ⚠ {msg}", file=sys.stderr)
    def error(self, msg): print(f"    ✗ {msg}", file=sys.stderr)


def _base_ydl_opts(output_dir: str) -> dict:
    # Opciones comunes a todos los descargadores: formato mp4, sin spam en consola
    return {
        'outtmpl': os.path.join(output_dir, 'original.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'logger': _YtdlpLogger(),
        'quiet': True,
        'no_warnings': True,
    }


def _collect_download(output_dir: str) -> str | None:
    # Devuelve la ruta del archivo descargado o None si no existe todavía
    for f in Path(output_dir).glob('original.*'):
        return str(f)
    return None


def _download_youtube(url: str, output_dir: str) -> str:
    # Cliente Android: evita el bloqueo anti-bot de YouTube sin necesitar cookies
    try:
        import yt_dlp
    except ImportError:
        error("yt-dlp no está instalado. Ejecuta: pip install yt-dlp")

    opts = _base_ydl_opts(output_dir)
    opts['extractor_args'] = {'youtube': {'player_client': ['android', 'web']}}

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        path = _collect_download(output_dir)
        if path:
            ok(f"Descargado: {Path(path).name}")
            return path
    except Exception as e:
        error(
            f"No se pudo descargar el video.\n"
            f"  Error: {e}\n"
            f"\n"
            f"  Posibles soluciones:\n"
            f"  - Verifica que la URL sea correcta y el video sea público\n"
            f"  - Actualiza yt-dlp: pip install -U yt-dlp\n"
            f"  - Usa un archivo local: python dubber.py ruta/al/video.mp4"
        )


def _download_vk(url: str, output_dir: str) -> str:
    # VK: intenta sin cookies primero (videos públicos), luego con cookies del navegador
    # IMPORTANTE: el navegador debe estar completamente cerrado al usar cookies,
    # de lo contrario Windows bloquea el archivo SQLite y la copia falla.
    try:
        import yt_dlp
    except ImportError:
        error("yt-dlp no está instalado. Ejecuta: pip install yt-dlp")

    opts = _base_ydl_opts(output_dir)

    # Intento 1: sin cookies (funciona para videos públicos de VK)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        path = _collect_download(output_dir)
        if path:
            ok(f"Descargado: {Path(path).name}")
            return path
    except Exception:
        for f in Path(output_dir).glob('original.*'):
            f.unlink(missing_ok=True)

    # Intento 2: cookies del navegador (necesario para videos privados o de grupo)
    # Edge se prueba primero porque en Windows 11 siempre está instalado
    last_exc = None
    for browser in ['edge', 'chrome', 'firefox']:
        try:
            browser_opts = dict(opts)
            browser_opts['cookiesfrombrowser'] = (browser,)
            with yt_dlp.YoutubeDL(browser_opts) as ydl:
                ydl.download([url])
            path = _collect_download(output_dir)
            if path:
                ok(f"Descargado con cookies de {browser}: {Path(path).name}")
                return path
        except Exception as e:
            last_exc = e
            for f in Path(output_dir).glob('original.*'):
                f.unlink(missing_ok=True)

    error(
        f"No se pudo descargar el video de VK.\n"
        f"  Error: {last_exc}\n"
        f"\n"
        f"  Soluciones:\n"
        f"  1. Cierra completamente Edge y Chrome, luego vuelve a intentar\n"
        f"     (Windows bloquea las cookies mientras el navegador está abierto)\n"
        f"  2. Verifica que el video sea accesible y tengas sesión iniciada en VK"
    )


def download_video(url: str, output_dir: str) -> str:
    # Enruta al descargador correcto según la plataforma
    step(f"Descargando video de {url}")
    if 'vk.com' in url or 'vkvideo.ru' in url:
        return _download_vk(url, output_dir)
    return _download_youtube(url, output_dir)


def extract_audio(video_path: str, audio_path: str):
    step("Extrayendo audio")
    # WAV PCM 16 kHz mono: formato exacto que espera Whisper para transcripción óptima
    run_ffmpeg([
        '-y', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        audio_path
    ], "Extracción de audio")
    ok()


def transcribe(audio_path: str, model_size: str, language: str = None) -> tuple:
    label = f"'{language}'" if language else "auto-detectado"
    step(f"Transcribiendo con Whisper '{model_size}' — idioma: {label} (primera vez descarga el modelo)")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        error("faster-whisper no está instalado. Ejecuta: pip install faster-whisper")

    # int8 en CPU: mucho más rápido que float32 con calidad prácticamente idéntica
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, language=language, beam_size=5)

    detected = info.language
    if not language:
        ok(f"Idioma detectado: {detected} (probabilidad: {info.language_probability:.0%})")

    # Conservar solo segmentos con texto real; cada uno incluye start/end en segundos
    result = [
        {'start': seg.start, 'end': seg.end, 'text': seg.text.strip()}
        for seg in segments
        if seg.text.strip()
    ]
    ok(f"{len(result)} segmentos transcritos")
    return result, detected


def translate(segments: list, source_lang: str) -> list:
    step(f"Traduciendo {source_lang} → español (Google Translate)")
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        error("deep-translator no está instalado. Ejecuta: pip install deep-translator")

    # Se traduce segmento a segmento para preservar los timestamps de Whisper
    translator = GoogleTranslator(source=source_lang, target='es')
    for seg in segments:
        seg['translated'] = translator.translate(seg['text']) if seg['text'] else ''

    ok(f"{len(segments)} segmentos traducidos")
    return segments


# Voces de Edge TTS garantizadas como español latinoamericano
# Se usan como fallback en orden si la voz principal no está disponible en la API
VOICES_LATAM = [
    "es-MX-JorgeNeural",   # México, hombre
    "es-MX-DaliaNeural",   # México, mujer
    "es-US-AlonsoNeural",  # EEUU, hombre
    "es-AR-TomasNeural",   # Argentina, hombre
]


async def validate_voice(voice: str) -> str:
    # Consulta en tiempo real qué voces tiene disponibles la API de Edge TTS
    # Evita que un nombre incorrecto cause fallo silencioso en todos los segmentos
    try:
        import edge_tts
        available = {v['ShortName'] for v in await edge_tts.list_voices()}
        if voice in available:
            return voice
        print(f"    ⚠ Voz '{voice}' no disponible.", file=sys.stderr)
        for v in VOICES_LATAM:
            if v in available:
                print(f"    → Usando voz alternativa: {v}", file=sys.stderr)
                return v
    except Exception:
        pass
    return voice


async def _tts_save(text: str, path: str, voice: str, semaphore: asyncio.Semaphore):
    try:
        import edge_tts
    except ImportError:
        error("edge-tts no está instalado. Ejecuta: pip install edge-tts")
    async with semaphore:
        # Hasta 3 reintentos por segmento para absorber errores de red transitorios
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(path)
                return
            except Exception as e:
                if attempt == 2:
                    # Mostrar el error en lugar de descartarlo en silencio
                    print(f"    ⚠ Segmento omitido (TTS falló: {e})", file=sys.stderr)
                    return
                await asyncio.sleep(1)


async def generate_all_tts(segments: list, tmp_dir: str, voice: str):
    voice = await validate_voice(voice)
    step(f"Generando voz con Edge TTS (voz: {voice})")
    # Semáforo de 10: limita las peticiones simultáneas a la API para evitar throttling
    semaphore = asyncio.Semaphore(10)
    tasks = []
    for i, seg in enumerate(segments):
        text = seg.get('translated', '').strip()
        if text and len(text) > 1:
            path = os.path.join(tmp_dir, f'tts_{i}.mp3')
            tasks.append(_tts_save(text, path, voice, semaphore))
    # Todos los segmentos se generan en paralelo (respetando el semáforo)
    await asyncio.gather(*tasks)
    ok(f"{len(tasks)} clips de voz generados")


def build_dubbed_audio(segments: list, total_duration_s: float, tmp_dir: str) -> str:
    step("Ensamblando pista de audio (estilo documental)")
    try:
        from pydub import AudioSegment
    except ImportError:
        error("pydub no está instalado. Ejecuta: pip install pydub")

    # Base silenciosa del mismo largo que el video original
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

        # Gap disponible = tiempo hasta que empieza la siguiente frase (o fin del video)
        # Define el límite máximo para este segmento sin que tape al siguiente parlamento
        if i + 1 < len(segments):
            next_start_ms = int(segments[i + 1]['start'] * 1000)
        else:
            next_start_ms = total_ms
        gap_ms = max(next_start_ms - start_ms, 1)  # evitar división por cero

        # Estilo documental: voz a velocidad natural siempre.
        # Solo se comprime si el TTS supera el gap completo hasta la siguiente frase.
        if len(tts_audio) > gap_ms and gap_ms > 200:
            ratio = len(tts_audio) / gap_ms
            tts_wav = os.path.join(tmp_dir, f'tts_{i}_raw.wav')
            tts_adj = os.path.join(tmp_dir, f'tts_{i}_adj.wav')
            tts_audio.export(tts_wav, format='wav')
            atempo = build_atempo_filter(ratio)
            run_ffmpeg([
                '-y', '-i', tts_wav, '-filter:a', atempo, tts_adj
            ], f"atempo segmento {i}")
            tts_audio = AudioSegment.from_wav(tts_adj)

        # Mezcla (overlay) el clip TTS sobre la base silenciosa en el timestamp correcto
        dubbed = dubbed.overlay(tts_audio, position=start_ms)

    out_wav = os.path.join(tmp_dir, 'dubbed.wav')
    dubbed.export(out_wav, format='wav')
    ok()
    return out_wav


def merge_video_audio(video_path: str, audio_path: str, output_path: str, bg_volume: float = 0.15):
    step(f"Combinando video con pista doblada (fondo original al {int(bg_volume * 100)}%)")
    # Mezcla el audio original reducido (fondo ambiental) con la pista TTS a volumen completo
    # normalize=0: evita que amix divida el volumen de cada input por el número de entradas
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
    ], "Mezcla de video y audio")
    ok(f"Video guardado: {output_path}")


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────

def dub(url: str, output_path: str = None, model_size: str = "base",
        voice: str = "es-MX-JorgeNeural", source_lang: str = None,
        bg_volume: float = 0.15):
    # bg_volume: nivel del audio original mezclado de fondo (0.0=silencio, 1.0=volumen completo)
    check_ffmpeg()

    # Acepta tanto URLs como rutas a archivos locales
    is_local = os.path.isfile(url)

    # tempfile.TemporaryDirectory limpia automáticamente todos los archivos intermedios al terminar
    with tempfile.TemporaryDirectory(prefix='dubber_') as tmp_dir:
        if is_local:
            step(f"Usando archivo local: {url}")
            video_path = url
            ok()
        else:
            video_path = download_video(url, tmp_dir)

        if not output_path:
            base = Path(video_path).stem
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Timestamp en el nombre para no sobreescribir doblajes anteriores del mismo video
            output_path = str(Path(__file__).parent / f"{base}_doblado_es_{ts}.mp4")

        audio_wav = os.path.join(tmp_dir, 'audio.wav')
        extract_audio(video_path, audio_wav)

        total_duration = get_video_duration(video_path)

        segments, detected_lang = transcribe(audio_wav, model_size, language=source_lang)
        if not segments:
            error("No se detectó habla en el video.")

        if detected_lang == 'es':
            error(
                "El video ya está en español. No es necesario traducirlo.\n"
                "  Si el idioma detectado es incorrecto, usa --idioma-origen <codigo>"
            )

        segments = translate(segments, detected_lang)

        asyncio.run(generate_all_tts(segments, tmp_dir, voice))

        dubbed_wav = build_dubbed_audio(segments, total_duration, tmp_dir)

        merge_video_audio(video_path, dubbed_wav, output_path, bg_volume=bg_volume)

    print(f"\n{'='*50}")
    print(f"  Doblaje completado -> {output_path}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Dobla videos a español latino con IA (auto-detecta el idioma de origen)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python dubber.py https://youtu.be/XXXX
  python dubber.py https://vk.com/video-XXXXXXX_XXXXXXX
  python dubber.py <URL> -o mi_video.mp4
  python dubber.py <URL> --modelo small
  python dubber.py <URL> --voz es-MX-DaliaNeural
  python dubber.py <URL> --idioma-origen ru
  python dubber.py <URL> --volumen-fondo 0.20
  python dubber.py ruta/al/video.mp4 --idioma-origen fr

Modelos Whisper (mejor calidad = mas lento):
  tiny | base | small | medium | large-v3

Voces latinoamericanas disponibles (Edge TTS):
  es-MX-JorgeNeural   (México, hombre)  <- por defecto
  es-MX-DaliaNeural   (México, mujer)
  es-US-AlonsoNeural  (EEUU, hombre)
  es-AR-TomasNeural   (Argentina, hombre)

Códigos de idioma ISO 639-1 comunes:
  ru (ruso)  en (inglés)  fr (francés)  de (alemán)
  zh (chino)  ja (japonés)  pt (portugués)  it (italiano)
        """
    )
    parser.add_argument('url', help='URL del video o ruta a archivo local')
    parser.add_argument('-o', '--output', help='Ruta del archivo de salida (.mp4)')
    parser.add_argument(
        '--modelo', default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large-v3'],
        help='Modelo Whisper a usar (default: base)'
    )
    parser.add_argument(
        '--voz', default='es-MX-JorgeNeural',
        help='Voz de Edge TTS (default: es-MX-JorgeNeural)'
    )
    parser.add_argument(
        '--idioma-origen', default=None, dest='idioma_origen',
        metavar='CODIGO',
        help='Código ISO 639-1 del idioma original (ej: ru, en, fr). Por defecto: auto-detectar'
    )
    parser.add_argument(
        '--volumen-fondo', default=0.15, type=float, dest='volumen_fondo',
        metavar='NIVEL',
        help='Volumen del audio original de fondo (0.0=silencio, 0.15=15%% por defecto, 1.0=completo)'
    )

    args = parser.parse_args()
    dub(args.url, args.output, args.modelo, args.voz,
        source_lang=args.idioma_origen, bg_volume=args.volumen_fondo)


if __name__ == '__main__':
    main()
