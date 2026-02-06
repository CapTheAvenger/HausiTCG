@echo off
setlocal enabledelayedexpansion

REM RESET_STATS.bat - Resets Limitless Online Scraper Statistics
REM Clears all CSV files to allow fresh data collection on next run

echo.
echo ============================================================
echo RESET LIMITLESS ONLINE SCRAPER STATISTICS
echo ============================================================
echo.

set "data_dir=%~dp0..\..\data"
set "dist_dir=%~dp0"

echo Resetting statistics in: %data_dir%
echo.

set "reset_count=0"

REM Delete CSV files from data folder
if exist "%data_dir%\limitless_online_decks.csv" (
    del "%data_dir%\limitless_online_decks.csv"
    echo ✓ Deleted: limitless_online_decks.csv ^(data^)
    set /a reset_count+=1
) else (
    echo ⊘ Not found: limitless_online_decks.csv ^(data^)
)

if exist "%data_dir%\limitless_online_decks_matchups.csv" (
    del "%data_dir%\limitless_online_decks_matchups.csv"
    echo ✓ Deleted: limitless_online_decks_matchups.csv ^(data^)
    set /a reset_count+=1
) else (
    echo ⊘ Not found: limitless_online_decks_matchups.csv ^(data^)
)

if exist "%data_dir%\limitless_online_decks_comparison.csv" (
    del "%data_dir%\limitless_online_decks_comparison.csv"
    echo ✓ Deleted: limitless_online_decks_comparison.csv ^(data^)
    set /a reset_count+=1
) else (
    echo ⊘ Not found: limitless_online_decks_comparison.csv ^(data^)
)

if exist "%data_dir%\limitless_online_decks_comparison.html" (
    del "%data_dir%\limitless_online_decks_comparison.html"
    echo ✓ Deleted: limitless_online_decks_comparison.html ^(data^)
    set /a reset_count+=1
) else (
    echo ⊘ Not found: limitless_online_decks_comparison.html ^(data^)
)

REM Delete HTML from dist folder
if exist "%dist_dir%limitless_online_decks_comparison.html" (
    del "%dist_dir%limitless_online_decks_comparison.html"
    echo ✓ Deleted: limitless_online_decks_comparison.html ^(dist^)
    set /a reset_count+=1
) else (
    echo ⊘ Not found: limitless_online_decks_comparison.html ^(dist^)
)

echo.
echo ============================================================
if !reset_count! gtr 0 (
    echo ✓ Reset complete! !reset_count! file^(s^) deleted.
    echo Next run will collect fresh data.
) else (
    echo ⊘ No files were reset.
)
echo ============================================================
echo.
pause
