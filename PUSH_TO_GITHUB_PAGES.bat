@echo off
echo ========================================
echo   GITHUB PAGES DEPLOYMENT
echo   HausiTCG-Landing Repository
echo ========================================
echo.

REM Set paths
set SOURCE=C:\Users\haush\OneDrive\Desktop\Hausi´s Pokemon TCG Analysis
set TARGET=C:\Users\haush\Desktop\HausiTCG-Landing

echo [1/4] Kopiere HTML und Config Files...
copy /Y "%SOURCE%\landing.html" "%TARGET%\index.html"
copy /Y "%SOURCE%\formats.json" "%TARGET%\formats.json"
copy /Y "%SOURCE%\pokemon_sets_mapping.csv" "%TARGET%\pokemon_sets_mapping.csv"
echo.

echo [2/4] Kopiere CSV Data Files...
if not exist "%TARGET%\data" mkdir "%TARGET%\data"
copy /Y "%SOURCE%\data\all_cards_database.csv" "%TARGET%\data\all_cards_database.csv"
copy /Y "%SOURCE%\data\all_cards_database.json" "%TARGET%\data\all_cards_database.json"
copy /Y "%SOURCE%\data\city_league_analysis.csv" "%TARGET%\data\city_league_analysis.csv"
copy /Y "%SOURCE%\data\city_league_archetypes.csv" "%TARGET%\data\city_league_archetypes.csv"
copy /Y "%SOURCE%\data\city_league_archetypes_comparison.csv" "%TARGET%\data\city_league_archetypes_comparison.csv"
copy /Y "%SOURCE%\data\city_league_archetypes_deck_stats.csv" "%TARGET%\data\city_league_archetypes_deck_stats.csv"
copy /Y "%SOURCE%\data\current_meta_card_data.csv" "%TARGET%\data\current_meta_card_data.csv"
copy /Y "%SOURCE%\data\limitless_analysis.csv" "%TARGET%\data\limitless_analysis.csv"
copy /Y "%SOURCE%\data\limitless_online_decks.csv" "%TARGET%\data\limitless_online_decks.csv"
copy /Y "%SOURCE%\data\limitless_online_decks_comparison.csv" "%TARGET%\data\limitless_online_decks_comparison.csv"
copy /Y "%SOURCE%\data\ace_specs.csv" "%TARGET%\data\ace_specs.csv"
echo.

echo [3/4] Git Add, Commit und Push...
cd /d "%TARGET%"
git add .
git commit -m "Update: Landing page + all CSV data files - %date% %time%"
git push origin main
echo.

echo [4/4] Fertig!
echo.
echo Deine Seite wird in 1-2 Minuten aktualisiert:
echo https://captheavenger.github.io/HausiTCG-Landing/
echo.
pause
