@echo off
REM Reset City League Archetype Statistics
REM This batch file deletes the previous statistics to start fresh

setlocal enabledelayedexpansion

REM Get the data directory (relative to this batch file)
for %%A in ("%~dp0..") do set "WORKSPACE_DIR=%%~fA"
set "DATA_DIR=%WORKSPACE_DIR%\data"

echo.
echo ============================================================
echo RESET CITY LEAGUE ARCHETYPE STATISTICS
echo ============================================================
echo.
echo This will delete the following files:
echo   - %DATA_DIR%\city_league_archetypes.csv
echo   - %DATA_DIR%\city_league_archetypes_comparison.csv
echo   - %DATA_DIR%\city_league_archetypes_deck_stats.csv
echo   - %DATA_DIR%\city_league_archetypes_comparison.html
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

REM Delete the files
if exist "%DATA_DIR%\city_league_archetypes.csv" (
    del "%DATA_DIR%\city_league_archetypes.csv"
    echo Deleted: city_league_archetypes.csv
)

if exist "%DATA_DIR%\city_league_archetypes_comparison.csv" (
    del "%DATA_DIR%\city_league_archetypes_comparison.csv"
    echo Deleted: city_league_archetypes_comparison.csv
)

if exist "%DATA_DIR%\city_league_archetypes_deck_stats.csv" (
    del "%DATA_DIR%\city_league_archetypes_deck_stats.csv"
    echo Deleted: city_league_archetypes_deck_stats.csv
)

if exist "%DATA_DIR%\city_league_archetypes_comparison.html" (
    del "%DATA_DIR%\city_league_archetypes_comparison.html"
    echo Deleted: city_league_archetypes_comparison.html
)

echo.
echo ============================================================
echo Reset complete! Next run will create fresh statistics.
echo ============================================================
echo.
pause
