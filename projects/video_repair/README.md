# VideoRepair — Reparador de vídeos corruptos

> **Autor:** Jordi Y Blanch

Herramienta de reparación de vídeos corruptos escrita en Python puro (sin dependencias externas).
Soporta MP4, MOV, AVI, MKV, WebM, MPG y VOB.

## Cómo funciona

Analiza la estructura interna del contenedor de vídeo y corrige los problemas más comunes:

- **MP4 / MOV**: reconstruye el átomo `moov`, ajusta offsets de chunks, inserta `ftyp` si falta
- **AVI**: reconstruye el índice `idx1` escaneando el bloque `movi`, corrige tamaño RIFF
- **MKV / WebM**: reconstruye `SeekHead`, marca el `Segment` como tamaño desconocido
- **MPG / MPEG**: elimina paquetes corruptos, trunca la cola de basura al final

## Requisitos

- Python 3.11+
- Sin dependencias externas

## Uso

```bash
# Diagnosticar un archivo
python main_repair.py --diagnose video.mp4

# Reparar un archivo
python main_repair.py --input video.mp4 --output C:\Reparados

# Reparar toda una carpeta
python main_repair.py --input C:\Recuperados --output C:\Reparados
```

## Estructura

```
video_repair/
├── main_repair.py     — CLI principal
├── repair_engine.py   — Orquestador
├── mp4_repair.py      — Reparador MP4 / MOV / M4V
├── avi_repair.py      — Reparador AVI
├── mkv_repair.py      — Reparador MKV / WebM
├── mpg_repair.py      — Reparador MPG / MPEG / VOB
└── utils.py           — Utilidades binarias comunes
```
