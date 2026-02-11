@echo off
cd /d "%~dp0"

echo.
echo ============================================================
echo RESET LIMITLESS ONLINE SCRAPER STATISTICS
echo ============================================================
echo.

setlocal enabledelayedexpansion
set count=0

REM Delete from data/ folder (all outputs are here now)
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

echo.
echo ============================================================
echo COMPLETED: Deleted %count% files from data/ folder
echo ============================================================
echo.
pause
