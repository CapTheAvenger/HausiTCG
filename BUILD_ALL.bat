@echo off
REM BUILD_ALL.bat - Rebuilds all three scrapers directly in dist/ (no subfolders)

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo BUILDING ALL SCRAPERS (Simple Structure)
echo ============================================================
echo.

REM Backup settings from dist folder (they are only here now!)
if not exist ".backup_settings" mkdir ".backup_settings"
if exist "dist\city_league_archetype_settings.json" copy /Y "dist\city_league_archetype_settings.json" ".backup_settings\" >nul
if exist "dist\limitless_online_settings.json" copy /Y "dist\limitless_online_settings.json" ".backup_settings\" >nul
if exist "dist\unified_card_settings.json" copy /Y "dist\unified_card_settings.json" ".backup_settings\" >nul
echo [Backup] Settings gesichert

REM Clean dist folder first
if exist "dist" (
    echo Cleaning dist folder...
    del /Q "dist\*.exe" 2>nul
    echo.
)

REM Build City League Archetype Scraper
echo [1/3] Building City League Archetype Scraper...
python -m PyInstaller city_league_archetype_scraper.spec --distpath dist --noconfirm
if %ERRORLEVEL%==0 (echo [OK] City League build successful) else (echo [ERROR] City League build failed & exit /b 1)
echo.

REM Build Limitless Online Scraper
echo [2/3] Building Limitless Online Scraper...
python -m PyInstaller limitless_online_scraper.spec --distpath dist --noconfirm
if %ERRORLEVEL%==0 (echo [OK] Limitless Online build successful) else (echo [ERROR] Limitless Online build failed & exit /b 1)
echo.

REM Build Unified Card Scraper
echo [3/3] Building Unified Card Scraper...
python -m PyInstaller unified_card_scraper.spec --distpath dist --noconfirm
if %ERRORLEVEL%==0 (echo [OK] Unified Card build successful) else (echo [ERROR] Unified Card build failed & exit /b 1)
echo.

REM Copy required files to dist
echo ============================================================
echo POST-BUILD: Copying required files
echo ============================================================
echo.

REM Restore settings from backup
if exist ".backup_settings\city_league_archetype_settings.json" (
    copy /Y ".backup_settings\city_league_archetype_settings.json" "dist\" >nul
    echo [OK] city_league_archetype_settings.json (restored)
)

if exist ".backup_settings\limitless_online_settings.json" (
    copy /Y ".backup_settings\limitless_online_settings.json" "dist\" >nul
    echo [OK] limitless_online_settings.json (restored)
)

if exist ".backup_settings\unified_card_settings.json" (
    copy /Y ".backup_settings\unified_card_settings.json" "dist\" >nul
    echo [OK] unified_card_settings.json (restored)
)

REM Clean up backup
if exist ".backup_settings" rmdir /S /Q ".backup_settings"

REM Copy card database
if exist "all_cards_database.csv" (
    copy /Y "all_cards_database.csv" "dist\" >nul
    echo [OK] all_cards_database.csv
)

REM Copy card_type_lookup.py
if exist "card_type_lookup.py" (
    copy /Y "card_type_lookup.py" "dist\" >nul
    echo [OK] card_type_lookup.py
)

echo.
echo ============================================================
echo [SUCCESS] ALL BUILDS COMPLETE!
echo ============================================================
echo.
echo EXE files are in: dist\
echo.
pause
