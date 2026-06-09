@echo off
:: setlocal: todas las variables son locales a esta ejecucion, sin residuos de corridas anteriores
setlocal
chcp 65001 >nul
:: Cambiar al directorio del .bat para que dubber.py siempre encuentre sus archivos
cd /d "%~dp0"

echo ============================================
echo   VIDEO DUBBER -- Espanol Latino
echo ============================================
echo.

:: Si se paso la URL como argumento la usa directamente, si no la pide
if "%~1"=="" (
    set /p URL="URL o ruta del video: "
) else (
    set URL=%~1
)

:: Idioma de origen: dejar vacio activa la auto-deteccion de Whisper
echo.
echo Idioma de origen ^(Enter = auto-detectar con Whisper^)
echo  ru=ruso  en=ingles  fr=frances  de=aleman  zh=chino  ja=japones
set LANG=
set /p LANG="Idioma: "

:: Seleccion de voz: todas las opciones son espanol latinoamericano
echo.
echo Voz ^(Enter = es-MX-JorgeNeural por defecto^)
echo  1. es-MX-JorgeNeural   ^(Mexico, hombre^)   [defecto]
echo  2. es-MX-DaliaNeural   ^(Mexico, mujer^)
echo  3. es-US-AlonsoNeural  ^(EEUU,   hombre^)
echo  4. es-AR-TomasNeural   ^(Argentina, hombre^)
set VOZ_OPT=
set /p VOZ_OPT="Opcion [1-4]: "

set VOZ=es-MX-JorgeNeural
if "%VOZ_OPT%"=="2" set VOZ=es-MX-DaliaNeural
if "%VOZ_OPT%"=="3" set VOZ=es-US-AlonsoNeural
if "%VOZ_OPT%"=="4" set VOZ=es-AR-TomasNeural

:: Modelo Whisper: mas grande = mejor transcripcion pero mas lento y mas RAM
echo.
echo Modelo Whisper ^(Enter = base^)
echo  tiny=rapido/peor  base=equilibrado  small=mejor/lento
set MODELO=base
set /p MODELO="Modelo: "
if "%MODELO%"=="" set MODELO=base

:: Volumen del audio original de fondo
echo.
echo Volumen de fondo ^(Enter = 15%% por defecto^)
echo  0  = sin sonido de fondo
echo  10 = muy suave
echo  15 = suave [defecto]
echo  25 = moderado
set BG=15
set /p BG="Volumen [0-100]: "
if "%BG%"=="" set BG=15
:: Convertir porcentaje entero a decimal que Python pueda leer (ej: 15 -> 0.15, 5 -> 0.05)
set /a BG_INT=%BG%
if %BG_INT% equ 0   set BG_VOL=0.0
if %BG_INT% equ 5   set BG_VOL=0.05
if %BG_INT% equ 10  set BG_VOL=0.10
if %BG_INT% equ 15  set BG_VOL=0.15
if %BG_INT% equ 20  set BG_VOL=0.20
if %BG_INT% equ 25  set BG_VOL=0.25
if %BG_INT% equ 30  set BG_VOL=0.30
if %BG_INT% equ 50  set BG_VOL=0.50
if %BG_INT% equ 100 set BG_VOL=1.0
:: Si el usuario ingresó un valor no listado, usar el porcentaje dividido manualmente
if not defined BG_VOL set BG_VOL=0.%BG_INT%

:: Construir flags opcionales
set LANG_ARG=
if not "%LANG%"=="" set LANG_ARG=--idioma-origen %LANG%

:: Resumen de lo que se va a ejecutar
echo.
echo --------------------------------------------
echo  Voz:    %VOZ%
echo  Modelo: %MODELO%
echo  Fondo:  %BG_INT%%%
if "%LANG%"=="" (
    echo  Idioma: auto-detectar
) else (
    echo  Idioma: %LANG%
)
echo --------------------------------------------
echo.

:: Lanzar el script con los parametros elegidos
"C:\Users\paast\AppData\Local\Python\pythoncore-3.11-64\python.exe" dubber.py "%URL%" --voz %VOZ% --modelo %MODELO% --volumen-fondo %BG_VOL% %LANG_ARG%

echo.
pause
endlocal
