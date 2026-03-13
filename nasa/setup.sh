#!/bin/bash
# setup.sh — Install dependencies for the NASA FramePilot plugin
# Run this once after dropping the plugin into FramePilot's plugins directory.
# Creates a self-contained Python venv inside the plugin folder.

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

# Create (or recreate) venv inside the plugin directory
echo "📦 Creating virtual environment…"
python3 -m venv "$SCRIPT_DIR/venv"
echo "✅ venv created at $SCRIPT_DIR/venv"

# Install dependencies into the venv
echo "📦 Installing Pillow into venv…"
"$SCRIPT_DIR/venv/bin/pip" install --quiet -r requirements.txt
echo "✅ Dependencies installed"

# Make scripts executable
chmod +x main.py run.sh
echo "✅ Scripts are executable"

echo ""
echo "──────────────────────────────────────────"
echo "🔑 Optional: Get a free NASA API key"
echo "   https://api.nasa.gov/"
echo "   Without a key, DEMO_KEY is used (~30 req/hr limit)."
echo ""
echo "📁 Plugin should be installed at:"
echo "   ~/Library/Application Support/FramePilot/plugins/nasa/"
echo ""
echo "Then open FramePilot → Sources → enable 'NASA Space & Earth'."
echo ""
