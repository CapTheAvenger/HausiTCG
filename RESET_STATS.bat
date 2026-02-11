@echo off
cd /d "%~dp0"

echo.
echo ============================================================
echo RESET ALL SCRAPER STATISTICS
echo ============================================================
echo.

setlocal enabledelayedexpansion
set count=0

REM Delete City League files from data/ folder
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

REM Delete Limitless Online files from data/ folder
if exist "data\limitless_online_decks.csv" (
    del "data\limitless_online_decks.csv"
    echo Deleted: data\limitless_online_decks.csv
    set /a count+=1
)

if exist "data\limitless_online_decks_matchups.csv" (
    del "data\limitless_online_decks_matchups.csv"
    echo Deleted: data\limitless_online_decks_matchups.csv
    set /a count+=1
)

if exist "data\limitless_online_decks_matchups 2.csv" (
    del "data\limitless_online_decks_matchups 2.csv"
    echo Deleted: data\limitless_online_decks_matchups 2.csv
    set /a count+=1
)

if exist "data\limitless_online_decks_comparison.csv" (
    del "data\limitless_online_decks_comparison.csv"
    echo Deleted: data\limitless_online_decks_comparison.csv
    set /a count+=1
)

if exist "data\limitless_online_decks_comparison.html" (
    del "data\limitless_online_decks_comparison.html"
    echo Deleted: data\limitless_online_decks_comparison.html
    set /a count+=1
)

if exist "data\limitless_online_decks_comparison_local.html" (
    del "data\limitless_online_decks_comparison_local.html"
    echo Deleted: data\limitless_online_decks_comparison_local.html
    set /a count+=1
)

if exist "data\limitless_online_decks.html" (
    del "data\limitless_online_decks.html"
    echo Deleted: data\limitless_online_decks.html
    set /a count+=1
)

REM Delete Unified Card Data files from data/ folder
if exist "data\unified_card_data.csv" (
    del "data\unified_card_data.csv"
    echo Deleted: data\unified_card_data.csv
    set /a count+=1
)

echo.
echo ============================================================
echo COMPLETED: Deleted %count% files from data/ folder
echo ============================================================
echo.
pause
