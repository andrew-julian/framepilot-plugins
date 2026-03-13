#!/bin/bash
# setup.sh — Install dependencies for the NASA FramePilot plugin
# Run this once after dropping the plugin into FramePilot's plugins directory.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "🚀 NASA plugin setup"
echo "──────────────────────────────────────────"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required."
    echo "   Install via Homebrew:  brew install python3"
    echo "   Or download from:      https://python.org"
    exit 1
fi

PY_VERSION=$(python3 --version 2>&1)
echo "✅ $PY_VERSION"

# Install Pillow
echo "📦 Installing dependencies (Pillow)…"
pip3 install --quiet --user -r requirements.txt && echo "✅ Dependencies installed"

# Make entry script executable
chmod +x main.py && echo "✅ main.py is executable"

echo ""
echo "──────────────────────────────────────────"
echo "🔑 Optional: Get a free NASA API key"
echo "   https://api.nasa.gov/"
echo "   Without a key, DEMO_KEY is used (~30 req/hr limit)."
echo ""
echo "📁 To install the plugin, this directory should be at:"
echo "   ~/Library/Application Support/FramePilot/plugins/nasa/"
echo ""
echo "   If it's not already there, run:"
echo '   cp -r "'"$SCRIPT_DIR"'" ~/Library/Application\ Support/FramePilot/plugins/nasa/'
echo ""
echo "Then open FramePilot → Sources → enable 'NASA Space & Earth'."
echo ""
