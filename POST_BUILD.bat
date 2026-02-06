@echo off
REM POST_BUILD.bat - Copies settings and RESET files after PyInstaller builds
REM Run this after building EXEs to ensure all required files are in place

echo.
echo ============================================================
echo POST-BUILD: Copying settings and helper files
echo ============================================================
echo.

set "base_dir=%~dp0"

echo Copying settings files...
copy "%base_dir%scripts\limitless_online_settings.json" "%base_dir%dist\limitless_online_scraper\" /Y >nul
if %ERRORLEVEL%==0 (echo ✓ limitless_online_settings.json) else (echo ✗ limitless_online_settings.json)

copy "%base_dir%scripts\unified_card_settings.json" "%base_dir%dist\unified_card_scraper\" /Y >nul
if %ERRORLEVEL%==0 (echo ✓ unified_card_settings.json) else (echo ✗ unified_card_settings.json)

echo.
echo Copying RESET_STATS.bat files...
copy "%base_dir%dist\city_league_archetype_scraper\RESET_STATS.bat" "%base_dir%dist\city_league_archetype_scraper\" /Y >nul
copy "%base_dir%dist\limitless_online_scraper\RESET_STATS.bat" "%base_dir%dist\limitless_online_scraper\" /Y >nul

echo.
echo ============================================================
echo ✓ Post-build tasks complete!
echo ============================================================
echo.
