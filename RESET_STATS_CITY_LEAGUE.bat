@echo off
cd /d "%~dp0"

echo.
echo ============================================================
echo RESET CITY LEAGUE ARCHETYPE SCRAPER STATISTICS
echo ============================================================
echo.

setlocal enabledelayedexpansion
set count=0

REM Delete from data/ folder (all outputs are here now)
if exist "data\city_league_archetypes.csv" (
    del "data\city_league_archetypes.csv"
    echo Deleted: data\city_league_archetypes.csv
    set /a count+=1
)

if exist "data\city_league_archetypes_deck_stats.csv" (
    del "data\city_league_archetypes_deck_stats.csv"
    echo Deleted: data\city_league_archetypes_deck_stats.csv
    set /a count+=1
)

if exist "data\city_league_archetypes_comparison.csv" (
    del "data\city_league_archetypes_comparison.csv"
    echo Deleted: data\city_league_archetypes_comparison.csv
    set /a count+=1
)

if exist "data\city_league_archetypes_comparison.html" (
    del "data\city_league_archetypes_comparison.html"
    echo Deleted: data\city_league_archetypes_comparison.html
    set /a count+=1
)

if exist "data\city_league_archetypes_comparison_local.html" (
    del "data\city_league_archetypes_comparison_local.html"
    echo Deleted: data\city_league_archetypes_comparison_local.html
    set /a count+=1
)

echo.
echo ============================================================
echo COMPLETED: Deleted %count% files from data/ folder
echo ============================================================
echo.
pause
