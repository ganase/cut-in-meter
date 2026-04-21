#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ./.venv/bin/python ]; then
  echo ".venv was not found. Run setup_macos.command first."
  echo
  read -r -p "Press Enter to exit..."
  exit 1
fi

if [ ! -f .env ]; then
  echo ".env was not found. Run setup_macos.command first."
  echo
  read -r -p "Press Enter to exit..."
  exit 1
fi

echo "Starting server at http://127.0.0.1:8000 ..."
./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
