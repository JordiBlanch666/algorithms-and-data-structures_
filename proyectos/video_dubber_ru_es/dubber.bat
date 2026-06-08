@echo off
:: Forzar UTF-8 para mostrar tildes y caracteres especiales correctamente en la consola
chcp 65001 >nul
:: Cambiar al directorio del .bat para que dubber.py siempre encuentre sus archivos
cd /d "%~dp0"

echo ============================================
echo   VIDEO DUBBER — Español Latino
echo ============================================
echo.

:: Si se pasó la URL como argumento al abrir el .bat la usa directamente,
:: si no, la pide de forma interactiva
if "%~1"=="" (
    set /p URL="URL o ruta del video: "
) else (
    set URL=%~1
)

:: Idioma de origen: dejar vacío activa la auto-detección de Whisper
echo.
echo Idioma de origen (Enter = auto-detectar con Whisper)
echo  ru=ruso  en=ingles  fr=frances  de=aleman  zh=chino  ja=japones
set /p LANG="Idioma: "

:: Selección de voz: todas las opciones son español latinoamericano
echo.
echo Voz (Enter = es-MX-JorgeNeural por defecto)
echo  1. es-MX-JorgeNeural   (Mexico, hombre)   [defecto]
echo  2. es-MX-DaliaNeural   (Mexico, mujer)
echo  3. es-US-AlonsoNeural  (EEUU,   hombre)
echo  4. es-AR-TomasNeural   (Argentina, hombre)
set /p VOZ_OPT="Opcion [1-4]: "

:: Asignar nombre de voz según la opción elegida; sin opción queda el defecto mexicano
if "%VOZ_OPT%"=="2" set VOZ=es-MX-DaliaNeural
if "%VOZ_OPT%"=="3" set VOZ=es-US-AlonsoNeural
if "%VOZ_OPT%"=="4" set VOZ=es-AR-TomasNeural
if not defined VOZ set VOZ=es-MX-JorgeNeural

:: Modelo Whisper: más grande = mejor transcripción pero más lento y más RAM
echo.
echo Modelo Whisper (Enter = base)
echo  tiny=rapido/peor  base=equilibrado  small=mejor/lento
set /p MODELO_OPT="Modelo: "
if "%MODELO_OPT%"=="" set MODELO_OPT=base

:: Construir el flag --idioma-origen solo si el usuario ingresó algo
set ARGS=
if defined LANG if not "%LANG%"=="" set ARGS=%ARGS% --idioma-origen %LANG%

:: Resumen de lo que se va a ejecutar
echo.
echo --------------------------------------------
echo  Voz:    %VOZ%
echo  Modelo: %MODELO_OPT%
if defined LANG if not "%LANG%"=="" echo  Idioma: %LANG%
if not defined LANG echo  Idioma: auto-detectar
echo --------------------------------------------
echo.

:: Lanzar el script con los parámetros elegidos
"C:\Users\paast\AppData\Local\Python\pythoncore-3.11-64\python.exe" dubber.py "%URL%" --voz %VOZ% --modelo %MODELO_OPT%%ARGS%

echo.
pause
