@echo off
REM BUILD_ALL.bat - Rebuilds all three scrapers and ensures files are in place

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo BUILDING ALL SCRAPERS
echo ============================================================
echo.

REM Build City League Archetype Scraper
echo [1/3] Building City League Archetype Scraper...
python -m PyInstaller city_league_archetype_scraper.spec --noconfirm
if %ERRORLEVEL%==0 (echo ✓ City League build successful) else (echo ✗ City League build failed & exit /b 1)
echo.

REM Build Limitless Online Scraper
echo [2/3] Building Limitless Online Scraper...
python -m PyInstaller limitless_online_scraper.spec --noconfirm
if %ERRORLEVEL%==0 (echo ✓ Limitless Online build successful) else (echo ✗ Limitless Online build failed & exit /b 1)
echo.

REM Build Unified Card Scraper
echo [3/3] Building Unified Card Scraper...
python -m PyInstaller unified_card_scraper.spec --noconfirm
if %ERRORLEVEL%==0 (echo ✓ Unified Card build successful) else (echo ✗ Unified Card build failed & exit /b 1)
echo.

REM Run post-build tasks
echo ============================================================
echo POST-BUILD: Copying required files
echo ============================================================
echo.
call POST_BUILD.bat

echo.
echo ============================================================
echo ✓ ALL BUILDS COMPLETE!
echo ============================================================
echo.
pause
