@echo off
:: setlocal: variables are local to this run, with nothing left over from earlier runs
setlocal
chcp 65001 >nul
:: Switch to the .bat folder so dubber.py can find its files
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
echo            AI-powered automatic video dubbing
echo  =====================================================
echo.

:: Use the URL if it was passed as an argument, otherwise ask for it
:: Supported platforms: YouTube, VK (vk.com / vkvideo.ru) and local files
if "%~1"=="" (
    echo Platforms: YouTube, VK ^(vk.com^), local file
    set /p URL="Video URL or path: "
) else (
    set URL=%~1
)

:: Source language: leaving it empty turns on Whisper auto-detection
echo.
echo Source language ^(Enter = auto-detect with Whisper^)
echo  ru=Russian  en=English  fr=French  de=German  zh=Chinese  ja=Japanese
set SRC_LANG=
set /p SRC_LANG="Language: "

:: Voice selection: every option is Latin American Spanish
echo.
echo Voice ^(Enter = es-MX-JorgeNeural by default^)
echo  1. es-MX-JorgeNeural   ^(Mexico, male^)     [default]
echo  2. es-MX-DaliaNeural   ^(Mexico, female^)
echo  3. es-US-AlonsoNeural  ^(USA,    male^)
echo  4. es-AR-TomasNeural   ^(Argentina, male^)
set VOICE_OPT=
set /p VOICE_OPT="Option [1-4]: "

set VOICE=es-MX-JorgeNeural
if "%VOICE_OPT%"=="2" set VOICE=es-MX-DaliaNeural
if "%VOICE_OPT%"=="3" set VOICE=es-US-AlonsoNeural
if "%VOICE_OPT%"=="4" set VOICE=es-AR-TomasNeural

:: Whisper model: bigger = better transcription but slower and more RAM
echo.
echo Whisper model ^(Enter = base^)
echo  tiny  = fast but less accurate
echo  base  = balance of quality and speed  [default]
echo  small = better quality, slower
set MODEL=base
set /p MODEL="Model: "
if "%MODEL%"=="" set MODEL=base

:: Volume of the original audio mixed in the background
echo.
echo Background volume ^(Enter = 15 by default^)
echo  0  = no background sound ^(dubbed voice only^)
echo  10 = very soft
echo  15 = soft [default]
echo  25 = moderate
echo  50 = loud
set BG=15
set /p BG="Volume [0-100]: "
if "%BG%"=="" set BG=15

:: Convert the whole-number percentage into a decimal Python can read
:: Single-digit values need a leading zero (e.g. 5 -> 0.05, not 0.5)
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
:: Fallback for two-digit values not listed above (e.g. 35 -> 0.35)
if not defined BG_VOL set BG_VOL=0.%BG_INT%

:: Only build the --source-lang flag if the user typed something
set LANG_ARG=
if not "%SRC_LANG%"=="" set LANG_ARG=--source-lang %SRC_LANG%

:: Settings summary before starting
echo.
echo ============================================
echo  SETTINGS
echo  Voice:    %VOICE%
echo  Model:    %MODEL%
echo  Backgr.:  %BG_INT%%%
if "%SRC_LANG%"=="" (
    echo  Language: auto-detect
) else (
    echo  Language: %SRC_LANG%
)
echo  Output:   same folder as this .bat
echo  Name:     ^<title^>_dubbed_es_^<date_time^>.mp4
echo  VK note:  close Edge/Chrome if the download fails
echo ============================================
echo.

:: Run the script with the chosen settings
python dubber.py "%URL%" --voice %VOICE% --model %MODEL% --bg-volume %BG_VOL% %LANG_ARG%

echo.
pause
endlocal
