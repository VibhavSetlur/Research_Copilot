#!/usr/bin/env bash
# Research Copilot — Environment Setup (Conda)
# Creates a reproducible Conda environment for the research project.
#
# Usage:
#   bash environment/setup_conda.sh          # Create conda env and install
#   bash environment/setup_conda.sh --clean  # Remove and recreate
#   conda activate research-copilot          # Activate

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_NAME="research-copilot"
REQUIREMENTS="$PROJECT_ROOT/environment/requirements.txt"

echo "============================================"
echo "  Research Copilot — Conda Environment Setup"
echo "============================================"
echo ""

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Install Miniconda or Anaconda first."
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check for --clean flag
if [ "$1" = "--clean" ]; then
    echo "Removing existing conda environment: $ENV_NAME"
    conda env remove -n "$ENV_NAME" -y
    echo "Done."
    echo ""
fi

# Check if env already exists
if conda env list | grep -q "^$ENV_NAME "; then
    echo "Conda environment '$ENV_NAME' already exists."
    echo "To recreate, run: bash environment/setup_conda.sh --clean"
    echo ""
    echo "To activate:"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "To install/update dependencies:"
    echo "  conda activate $ENV_NAME"
    echo "  pip install -r $REQUIREMENTS"
    exit 0
fi

# Create conda environment
echo "Creating conda environment: $ENV_NAME"
conda create -n "$ENV_NAME" python=3.11 -y
echo "Done."
echo ""

# Activate and install dependencies
echo "Installing dependencies..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"
pip install --upgrade pip
pip install -r "$REQUIREMENTS"
echo ""

echo "============================================"
echo "  Setup Complete"
echo "============================================"
echo ""
echo "To activate the environment:"
echo "  conda activate $ENV_NAME"
echo ""
echo "To run the research CLI:"
echo "  python .research/research.py status"
echo ""
echo "To run analysis scripts:"
echo "  python .research/scripts/utils/cache_manager.py --stats"
echo ""
