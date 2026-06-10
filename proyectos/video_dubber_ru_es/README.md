# Video Dubber → Español Latino

Herramienta de doblaje automático que descarga videos de **YouTube** o **VK** y genera una versión doblada al **español latinoamericano** usando inteligencia artificial. El idioma de origen se detecta automáticamente — funciona con ruso, inglés, francés, alemán y cualquier idioma soportado por Whisper.

El resultado suena como un **doblaje de documental**: la voz doblada va a velocidad natural, mientras el audio original (música, ambiente) se conserva a bajo volumen de fondo.

## Pipeline

```
URL del video (YouTube o VK) — o archivo local
    │
    ├─ youtube.com / youtu.be ──► cliente Android de yt-dlp (sin cookies)
    └─ vk.com / vkvideo.ru ─────► sin cookies → cookies de Edge → Chrome → Firefox
    │
    ▼
Extracción de audio WAV 16 kHz mono (ffmpeg)
    │
    ▼
Transcripción + detección de idioma (faster-whisper)
    │
    ▼
Traducción X → ES (Google Translate)
    │
    ▼
Síntesis de voz en español latino (Edge TTS)
    │
    ▼
Ensamblaje estilo documental — voz a velocidad natural (pydub + ffmpeg)
    │
    ▼
Mezcla: voz doblada (100%) + audio original de fondo (15%) (ffmpeg)
    │
    ▼
Video doblado (.mp4)
```

## Requisitos previos

- **Python 3.9+**
- **ffmpeg** (debe estar en el PATH del sistema)

### Instalar ffmpeg en Windows

1. Descarga la versión *release full* desde [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extrae el ZIP en una carpeta (p.ej. `C:\ffmpeg`)
3. Añade `C:\ffmpeg\bin` a las variables de entorno → PATH

Verifica que funciona:

```bash
ffmpeg -version
```

## Instalación

```bash
cd proyectos/video_dubber_ru_es
pip install -r requirements.txt
```

## Uso rápido — dubber.bat

Doble clic en `dubber.bat`. El asistente interactivo pregunta paso a paso:

1. URL del video (YouTube o VK) o ruta a un archivo local
2. Idioma de origen (Enter = auto-detectar)
3. Voz latinoamericana (menú 1–4)
4. Modelo Whisper (calidad de transcripción)
5. Volumen del audio de fondo (0–100%)

> **VK con videos privados o de grupo:** si el script no puede descargar el video, cierra completamente Edge o Chrome y vuelve a intentar. Windows bloquea el archivo de cookies mientras el navegador está abierto.

## Uso por línea de comandos

```bash
python dubber.py <URL> [opciones]
```

### Ejemplos

```bash
# YouTube — auto-detectar idioma
python dubber.py https://youtu.be/XXXX

# VK — auto-detectar idioma
python dubber.py https://vk.com/video-XXXXXXX_XXXXXXX

# Forzar idioma de origen
python dubber.py https://youtu.be/XXXX --idioma-origen en
python dubber.py https://vk.com/video-XXXX --idioma-origen ru

# Especificar archivo de salida
python dubber.py <URL> -o mi_video_doblado.mp4

# Mayor calidad de transcripción
python dubber.py <URL> --modelo small

# Cambiar voz del doblaje
python dubber.py <URL> --voz es-MX-DaliaNeural

# Ajustar volumen del audio de fondo (0.0 = silencio, 1.0 = original completo)
python dubber.py <URL> --volumen-fondo 0.20

# Usar archivo local en vez de URL
python dubber.py ruta/al/video.mp4 --idioma-origen fr
```

El primer uso descarga el modelo Whisper `base` (~150 MB).

El archivo de salida se guarda en la misma carpeta del script con el formato `<nombre>_doblado_es_YYYYMMDD_HHMMSS.mp4` para no sobreescribir doblajes anteriores del mismo video.

## Opciones

| Argumento | Descripción | Por defecto |
|-----------|-------------|-------------|
| `url` | URL del video (YouTube o VK) o ruta a archivo local | *(obligatorio)* |
| `-o`, `--output` | Ruta del archivo de salida (`.mp4`) | `<nombre>_doblado_es_<timestamp>.mp4` |
| `--modelo` | Modelo Whisper para transcripción | `base` |
| `--voz` | Voz de Edge TTS para el doblaje | `es-MX-JorgeNeural` |
| `--idioma-origen` | Código ISO 639-1 del idioma original (`ru`, `en`, `fr`…). Por defecto auto-detecta. | auto |
| `--volumen-fondo` | Volumen del audio original mezclado de fondo (`0.0`–`1.0`) | `0.15` |

## Descarga de videos VK

Para videos públicos de VK no se necesita ninguna configuración adicional.

Para videos privados o de grupo, el script intenta automáticamente leer las cookies de Edge, Chrome y Firefox (en ese orden). Si falla:

1. **Cierra completamente** Edge o Chrome antes de ejecutar el script
2. Vuelve a intentar — yt-dlp podrá acceder al archivo de cookies sin que el navegador lo bloquee

## Idiomas de origen soportados

Cualquier idioma que reconozca Whisper. Códigos comunes:

| Código | Idioma |
|--------|--------|
| `ru` | Ruso |
| `en` | Inglés |
| `fr` | Francés |
| `de` | Alemán |
| `zh` | Chino |
| `ja` | Japonés |
| `pt` | Portugués |
| `it` | Italiano |

## Modelos Whisper

| Modelo | Tamaño | Velocidad | Calidad |
|--------|--------|-----------|---------|
| `tiny` | ~75 MB | Muy rápido | Básica |
| `base` | ~150 MB | Rápido | Buena *(por defecto)* |
| `small` | ~500 MB | Moderado | Muy buena |
| `medium` | ~1.5 GB | Lento | Excelente |
| `large-v3` | ~3 GB | Muy lento | Máxima |

## Voces disponibles (español latino)

| Voz | Variante | Género |
|-----|----------|--------|
| `es-MX-JorgeNeural` | México | Hombre *(por defecto)* |
| `es-MX-DaliaNeural` | México | Mujer |
| `es-US-AlonsoNeural` | EEUU | Hombre |
| `es-AR-TomasNeural` | Argentina | Hombre |

> El script valida automáticamente que la voz esté disponible en Edge TTS y usa la siguiente de la lista si no lo está.

## Dependencias

| Librería | Versión mínima | Función |
|----------|---------------|---------|
| `yt-dlp` | 2024.1.1 | Descarga videos de YouTube y VK |
| `faster-whisper` | 1.0.0 | Transcripción y detección automática de idioma |
| `deep-translator` | 1.11.4 | Traducción al español (Google Translate) |
| `edge-tts` | 6.1.9 | Síntesis de voz en español latino |
| `pydub` | 0.25.1 | Manipulación y ensamblaje de audio |
| `ffmpeg` | — | Procesamiento de video/audio (externo) |
