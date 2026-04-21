@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Checking Python...
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
  py -3.13 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.13"
  if not defined PYTHON_CMD py -3.12 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.12"
  if not defined PYTHON_CMD py -3.11 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.11"
)

if not defined PYTHON_CMD where python3.13 >nul 2>nul && set "PYTHON_CMD=python3.13"
if not defined PYTHON_CMD where python3.12 >nul 2>nul && set "PYTHON_CMD=python3.12"
if not defined PYTHON_CMD where python3.11 >nul 2>nul && set "PYTHON_CMD=python3.11"

if not defined PYTHON_CMD (
  echo.
  echo Supported Python was not found.
  echo Please install Python 3.11, 3.12, or 3.13, then run this file again.
  echo.
  pause
  exit /b 1
)

echo [2/4] Creating virtual environment...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
  echo Failed to create .venv
  pause
  exit /b 1
)

echo [3/4] Installing dependencies...
call .venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip
  pause
  exit /b 1
)

call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install requirements.txt
  pause
  exit /b 1
)

echo [4/4] Preparing .env...
if not exist .env (
  copy /Y .env.example .env >nul
)

echo.
echo Setup completed.
echo Next:
echo 1. Open .env and set OPENAI_API_KEY
echo 2. Run run_windows.bat
echo.
pause
