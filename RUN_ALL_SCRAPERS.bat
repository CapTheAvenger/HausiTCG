@echo off
chcp 65001 >nul
cls
echo ============================================================
echo              UNIFIED SCRAPER TCG - Quick Start
echo ============================================================
echo.
echo Startet alle Scraper nacheinander:
echo   1. City League Archetype Scraper
echo   2. Limitless Online Scraper
echo   3. Unified Card Scraper
echo.
echo ============================================================
pause

echo.
echo ============================================================
echo [1/3] Starte City League Archetype Scraper...
echo ============================================================
cd "dist\city_league_archetype_scraper"
start /wait city_league_archetype_scraper.exe
cd ..\..

echo.
echo ============================================================
echo [2/3] Starte Limitless Online Scraper...
echo ============================================================
cd "dist\limitless_online_scraper"
start /wait limitless_online_scraper.exe
cd ..\..

echo.
echo ============================================================
echo [3/3] Starte Unified Card Scraper...
echo ============================================================
cd "dist\unified_card_scraper"
start /wait unified_card_scraper.exe
cd ..\..

echo.
echo ============================================================
echo              ALLE SCRAPER ABGESCHLOSSEN!
echo ============================================================
echo.
echo Ergebnisse findest du im "data\" Ordner:
echo   - city_league_archetypes.csv + HTML
echo   - limitless_online_decks.csv + HTML
echo   - unified_card_data.csv
echo.
echo ============================================================
pause
