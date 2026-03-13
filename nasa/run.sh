#!/bin/bash
# run.sh — FramePilot plugin entry point
# Activates the local venv and runs main.py.
# FramePilot calls this script; it must write PNG bytes to stdout.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"

if [ ! -f "$PYTHON" ]; then
    echo "venv not found. Run setup.sh first: bash $SCRIPT_DIR/setup.sh" >&2
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/main.py"
