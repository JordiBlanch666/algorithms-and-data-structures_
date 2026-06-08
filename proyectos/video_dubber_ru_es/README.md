# Video Dubber → Español

Herramienta de doblaje automático que descarga videos de VK, YouTube u otras plataformas y genera una versión doblada al español usando inteligencia artificial. **El idioma de origen se detecta automáticamente** — funciona con ruso, inglés, francés, alemán y cualquier idioma soportado por Whisper.

## Pipeline

```
URL del video (o archivo local)
    │
    ▼
Descarga (yt-dlp)
    │
    ▼
Extracción de audio (ffmpeg)
    │
    ▼
Transcripción + detección de idioma (faster-whisper)
    │
    ▼
Traducción X → ES (Google Translate)
    │
    ▼
Síntesis de voz en español (Edge TTS)
    │
    ▼
Ensamblaje y sincronización (pydub + ffmpeg)
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

## Uso

```bash
python dubber.py <URL> [opciones]
```

### Ejemplos

```bash
# Auto-detectar idioma (recomendado)
python dubber.py https://vk.com/video-XXXXXXX_XXXXXXX

# Forzar idioma de origen
python dubber.py https://youtu.be/XXXX --idioma-origen en
python dubber.py https://vk.com/video-XXXX --idioma-origen ru

# Especificar archivo de salida
python dubber.py https://vk.com/video-XXXX -o mi_video_doblado.mp4

# Mayor calidad de transcripción
python dubber.py <URL> --modelo small

# Cambiar voz del doblaje
python dubber.py <URL> --voz es-MX-JorgeNeural

# Usar archivo local en vez de URL
python dubber.py ruta/al/video.mp4 --idioma-origen fr

# VK con cookies del navegador
python dubber.py <URL> --navegador edge
python dubber.py <URL> --cookies cookies.txt
```

El primer uso descarga el modelo Whisper `base` (~150 MB).

## Opciones

| Argumento | Descripción | Por defecto |
|-----------|-------------|-------------|
| `url` | URL del video o ruta a archivo local | *(obligatorio)* |
| `-o`, `--output` | Ruta del archivo de salida (`.mp4`) | `<nombre>_doblado_es.mp4` |
| `--modelo` | Modelo Whisper para transcripción | `base` |
| `--voz` | Voz de Edge TTS para el doblaje | `es-ES-AlvaroNeural` |
| `--idioma-origen` | Código ISO 639-1 del idioma original (`ru`, `en`, `fr`…). Por defecto auto-detecta. | auto |
| `--navegador` | Navegador del que tomar cookies de VK (`chrome`, `edge`, `firefox`…) | auto |
| `--cookies` | Ruta a un archivo `cookies.txt` exportado manualmente | — |

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

## Voces disponibles

| Voz | Variante | Género |
|-----|----------|--------|
| `es-ES-AlvaroNeural` | España | Hombre *(por defecto)* |
| `es-ES-ElviraNeural` | España | Mujer |
| `es-MX-JorgeNeural` | México | Hombre |
| `es-MX-DaliaNeural` | México | Mujer |
| `es-AR-TomasNeural` | Argentina | Hombre |

## Dependencias

| Librería | Versión mínima | Función |
|----------|---------------|---------|
| `yt-dlp` | 2024.1.1 | Descarga videos de plataformas web |
| `faster-whisper` | 1.0.0 | Transcripción y detección automática de idioma |
| `deep-translator` | 1.11.4 | Traducción al español (Google Translate) |
| `edge-tts` | 6.1.9 | Síntesis de voz en español |
| `pydub` | 0.25.1 | Manipulación y ensamblaje de audio |
| `ffmpeg` | — | Procesamiento de video/audio (externo) |
