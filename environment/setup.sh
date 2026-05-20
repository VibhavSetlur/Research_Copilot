#!/usr/bin/env bash
# Research Copilot — Environment Setup (venv)
# Creates a reproducible Python environment for the research project.
#
# Usage:
#   bash environment/setup.sh          # Create venv and install
#   bash environment/setup.sh --clean  # Remove and recreate
#   source environment/venv/bin/activate  # Activate

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_DIR="$PROJECT_ROOT/environment/venv"
REQUIREMENTS="$PROJECT_ROOT/environment/requirements.txt"

echo "============================================"
echo "  Research Copilot — Environment Setup"
echo "============================================"
echo ""

# Check for --clean flag
if [ "$1" = "--clean" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$ENV_DIR"
    echo "Done."
    echo ""
fi

# Check if venv already exists
if [ -d "$ENV_DIR" ]; then
    echo "Virtual environment already exists at: $ENV_DIR"
    echo "To recreate, run: bash environment/setup.sh --clean"
    echo ""
    echo "To activate:"
    echo "  source $ENV_DIR/bin/activate"
    echo ""
    echo "To install/update dependencies:"
    echo "  source $ENV_DIR/bin/activate"
    echo "  pip install -r $REQUIREMENTS"
    exit 0
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$ENV_DIR"
echo "Done."
echo ""

# Activate and install dependencies
echo "Activating environment and installing dependencies..."
source "$ENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$REQUIREMENTS"
echo ""

echo "============================================"
echo "  Setup Complete"
echo "============================================"
echo ""
echo "To activate the environment:"
echo "  source $ENV_DIR/bin/activate"
echo ""
echo "To run the research CLI:"
echo "  python .research/research.py status"
echo ""
echo "To run analysis scripts:"
echo "  python .research/scripts/utils/cache_manager.py --stats"
echo ""
