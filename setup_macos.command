#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[1/4] Checking Python..."
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo
  echo "Python was not found."
  echo "Please install Python 3.11 or later, then run this file again."
  echo
  read -r -p "Press Enter to exit..."
  exit 1
fi

if ! "$PYTHON_CMD" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)'; then
  echo
  echo "Unsupported Python version was found."
  echo "Please install Python 3.11, 3.12, or 3.13, then run this file again."
  echo
  read -r -p "Press Enter to exit..."
  exit 1
fi

echo "[2/4] Creating virtual environment..."
"$PYTHON_CMD" -m venv .venv

echo "[3/4] Installing dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

echo "[4/4] Preparing .env..."
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo
echo "Setup completed."
echo "Next:"
echo "1. Open .env and set OPENAI_API_KEY"
echo "2. Run run_macos.command"
echo
read -r -p "Press Enter to exit..."
