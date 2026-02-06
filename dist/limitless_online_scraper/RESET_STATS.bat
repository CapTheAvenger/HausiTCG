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
set "files_to_reset=limitless_online_decks.csv limitless_online_decks_matchups.csv limitless_online_decks_comparison.csv"

echo Resetting statistics in: %data_dir%
echo.

set "reset_count=0"
for %%f in (%files_to_reset%) do (
    set "file_path=%data_dir%\%%f"
    if exist "!file_path!" (
        del "!file_path!"
        echo ✓ Deleted: %%f
        set /a reset_count+=1
    ) else (
        echo ⊘ Not found: %%f
    )
)

echo.
echo ============================================================
if %reset_count% gtr 0 (
    echo ✓ Reset complete! %reset_count% file^(s^) deleted.
    echo Next run will collect fresh data.
) else (
    echo ⊘ No files were reset.
)
echo ============================================================
echo.
pause
