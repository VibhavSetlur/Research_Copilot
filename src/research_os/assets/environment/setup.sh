#!/usr/bin/env bash
set -euo pipefail

# Research OS — Environment Setup Script

echo "Setting up Research OS environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment ready. Activate with: source venv/bin/activate"
