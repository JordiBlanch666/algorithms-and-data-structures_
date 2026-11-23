@echo off
:: setlocal: variables locales a esta ejecucion, sin residuos de corridas anteriores
setlocal
chcp 65001 >nul
:: Cambiar al directorio del .bat para que dubber.py encuentre sus archivos
cd /d "%~dp0"
cls

echo.
echo       ####  ###   #    ##   #  #   ###  #  #
echo          #  #  #  #   #  #  ## #  #    #  #
echo          #  ###   #   ####  # ##  #    ####
echo       #  #  #  #  #   #  #  #  #  #    #  #
echo        ###  ###  ####  #  #  #  #   ###  #  #
echo.
echo            = = = = =  D U B B E R  = = = = =
echo          Doblaje automatico de video con IA
echo  =====================================================
echo.

:: Si se paso la URL como argumento la usa directamente, si no la pide
:: Plataformas soportadas: YouTube, VK (vk.com / vkvideo.ru) y archivos locales
if "%~1"=="" (
    echo Plataformas: YouTube, VK ^(vk.com^), archivo local
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
echo  tiny = rapido pero menos preciso
echo  base = equilibrio calidad/velocidad  [defecto]
echo  small = mejor calidad, mas lento
set MODELO=base
set /p MODELO="Modelo: "
if "%MODELO%"=="" set MODELO=base

:: Volumen del audio original mezclado como fondo
echo.
echo Volumen de fondo ^(Enter = 15 por defecto^)
echo  0  = sin sonido de fondo ^(solo voz doblada^)
echo  10 = muy suave
echo  15 = suave [defecto]
echo  25 = moderado
echo  50 = alto
set BG=15
set /p BG="Volumen [0-100]: "
if "%BG%"=="" set BG=15

:: Convertir porcentaje entero a decimal que Python pueda leer
:: Valores de un digito necesitan cero adelante (ej: 5 -> 0.05, no 0.5)
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
:: Fallback para valores de dos digitos no listados (ej: 35 -> 0.35)
if not defined BG_VOL set BG_VOL=0.%BG_INT%

:: Construir flag --idioma-origen solo si el usuario ingreso algo
set LANG_ARG=
if not "%LANG%"=="" set LANG_ARG=--idioma-origen %LANG%

:: Resumen de configuracion antes de iniciar
echo.
echo ============================================
echo  CONFIGURACION
echo  Voz:    %VOZ%
echo  Modelo: %MODELO%
echo  Fondo:  %BG_INT%%%
if "%LANG%"=="" (
    echo  Idioma: auto-detectar
) else (
    echo  Idioma: %LANG%
)
echo  Salida: misma carpeta que este .bat
echo  Nombre: ^<titulo^>_doblado_es_^<fecha_hora^>.mp4
echo  Nota VK: cierra Edge/Chrome si falla la descarga
echo ============================================
echo.

:: Lanzar el script con los parametros elegidos
"C:\Users\paast\AppData\Local\Python\pythoncore-3.11-64\python.exe" dubber.py "%URL%" --voz %VOZ% --modelo %MODELO% --volumen-fondo %BG_VOL% %LANG_ARG%

echo.
pause
endlocal
