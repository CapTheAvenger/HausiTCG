@echo off
chcp 65001 >nul
cls
echo ============================================================
echo            DECK VIEWER - HTML Viewer öffnen
echo ============================================================
echo.
echo Öffnet den Deck Viewer im Browser...
echo.

REM Öffne den HTML Viewer im Standard-Browser
start "" "deck_viewer.html"

echo.
echo Deck Viewer wurde im Browser geöffnet!
echo.
echo Du kannst dort die CSV-Dateien aus dem "data\" Ordner laden:
echo   - city_league_archetypes_comparison.html
echo   - limitless_online_decks_comparison.html
echo   - unified_card_data.csv
echo.
echo ============================================================
timeout /t 3 >nul
