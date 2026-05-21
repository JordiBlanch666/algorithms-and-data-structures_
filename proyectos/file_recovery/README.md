# MediaRecover — Recuperador profundo de imágenes y vídeos eliminados

> **Autor:** Jordi Y Blanch

Herramienta de recuperación forense escrita en Python puro (sin dependencias externas).  
Trabaja directamente sobre los sectores crudos del disco mediante la API Win32.

## Cómo funciona

### Método 1 — Análisis del MFT (NTFS)
Lee la **Master File Table** del sistema de archivos NTFS para encontrar
entradas de archivos marcados como eliminados. Si los data runs (clusters de datos)
aún no han sido sobreescritos, reconstruye el archivo completo.

```
Disco → Boot Sector → MFT offset → Entradas FILE → Data Runs → Archivo
```

### Método 2 — File Carving
Escanea **cada sector del disco** en busca de firmas (magic bytes) conocidas,
completamente independiente del sistema de archivos. Funciona incluso en
discos formateados o con MFT dañada.

```
Disco → Sectores crudos → Magic bytes → Estimación de tamaño → Archivo
```

## Formatos soportados

### Imágenes
| Extensión | Descripción |
|-----------|-------------|
| JPG/JPEG  | JPEG / JFIF / EXIF |
| PNG       | Portable Network Graphics |
| GIF       | GIF87a / GIF89a |
| BMP       | Windows Bitmap |
| TIF/TIFF  | Tagged Image File Format |
| WebP      | Google WebP |
| HEIC/HEIF | Apple HEIC (iPhone) |
| CR2/CR3   | Canon RAW |
| NEF       | Nikon RAW |
| ARW       | Sony RAW |
| DNG       | Adobe DNG |
| ORF       | Olympus RAW |
| RW2       | Panasonic RAW |

### Vídeos
| Extensión | Descripción |
|-----------|-------------|
| MP4       | MPEG-4 (múltiples variantes) |
| MOV       | Apple QuickTime |
| AVI       | Audio Video Interleave |
| MKV       | Matroska / WebM |
| WMV       | Windows Media Video |
| FLV       | Flash Video |
| MPG/MPEG  | MPEG-1/2 |
| 3GP       | Mobile Video |
| MTS/M2TS  | AVCHD (cámaras Sony/Panasonic) |
| VOB       | DVD Video Object |

## Requisitos

- Python 3.11+
- Windows (usa API Win32 directamente)
- **Ejecutar como Administrador** (necesario para leer sectores crudos)

## Instalación

No requiere instalar ninguna librería externa.

```bash
git clone <repositorio>
cd proyectos/file_recovery
```

## Uso

### Listar discos disponibles
```bash
python main.py --list-disks
```

### Recuperar todo de la unidad C:
```bash
python main.py --disk C: --output D:\Recuperados
```

### Solo imágenes, solo file carving (más profundo)
```bash
python main.py --disk C: --output D:\Recuperados --only-images --only-carving
```

### Disco físico completo (incluye espacio no particionado)
```bash
python main.py --disk PhysicalDrive0 --output D:\Recuperados
```

### Solo vídeos grandes (mínimo 10 MB)
```bash
python main.py --disk C: --output D:\Recuperados --only-videos --min-size 10000000
```

## Estructura del proyecto

```
file_recovery/
├── main.py             # CLI y punto de entrada
├── disk_reader.py      # Acceso de bajo nivel al disco (Win32 API)
├── mft_parser.py       # Parser de la Master File Table NTFS
├── file_carver.py      # Escáner de firmas por sectores crudos
├── signatures.py       # Base de datos de magic bytes (imágenes + vídeos)
├── recovery_engine.py  # Orquestador: coordina ambos métodos
└── README.md
```

## Estructura de salida

```
D:\Recuperados\
├── mft\
│   ├── images\     ← archivos recuperados por MFT
│   └── videos\
└── carving\
    ├── images\     ← archivos recuperados por carving
    ├── videos\
    └── raw\
```

## Consideraciones importantes

- **Actúa rápido**: cuanto más tiempo pase desde el borrado, mayor es la
  probabilidad de que los sectores hayan sido sobreescritos.
- **No escribas en el disco a recuperar**: instala Python y ejecuta el script
  desde otro disco o live USB.
- El carving puede generar **falsos positivos** (archivos corruptos o parciales).
  Es normal; revisa los resultados con un visor de imágenes.
- Los archivos RAW de cámara (CR2, NEF, ARW) son similares a TIFF y pueden
  requerir Adobe Camera Raw o el software de la cámara para abrirse.
