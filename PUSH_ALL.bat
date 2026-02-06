@echo off
setlocal

echo [INFO] Checking for running scrapers...
tasklist /FI "IMAGENAME eq limitless_online_scraper.exe" | find /I "limitless_online_scraper.exe" >nul
if %errorlevel%==0 (
  echo [ERROR] limitless_online_scraper.exe is still running. Please wait and try again.
  exit /b 1
)
tasklist /FI "IMAGENAME eq unified_card_scraper.exe" | find /I "unified_card_scraper.exe" >nul
if %errorlevel%==0 (
  echo [ERROR] unified_card_scraper.exe is still running. Please wait and try again.
  exit /b 1
)
tasklist /FI "IMAGENAME eq city_league_archetype_scraper.exe" | find /I "city_league_archetype_scraper.exe" >nul
if %errorlevel%==0 (
  echo [ERROR] city_league_archetype_scraper.exe is still running. Please wait and try again.
  exit /b 1
)

echo [INFO] Syncing with origin/main...
git pull --rebase origin main
if %errorlevel% neq 0 (
  echo [ERROR] Pull failed. Resolve conflicts and try again.
  exit /b 1
)

echo [INFO] Staging changes...
git add -A

git diff --cached --quiet
if %errorlevel%==0 (
  echo [INFO] No changes to commit.
  exit /b 0
)

echo [INFO] Committing...
git commit -m "Update data & reports (auto)"

echo [INFO] Pushing to origin/main...
git push -u origin main

echo [INFO] Done.
endlocal
