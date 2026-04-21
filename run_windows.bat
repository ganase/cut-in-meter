@echo off
setlocal

cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo .venv was not found. Run setup_windows.bat first.
  echo.
  pause
  exit /b 1
)

if not exist .env (
  echo .env was not found. Run setup_windows.bat first.
  echo.
  pause
  exit /b 1
)

echo Starting server at http://127.0.0.1:8000 ...
echo If the browser does not open automatically, open:
echo http://127.0.0.1:8000
start "" http://127.0.0.1:8000
call .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
