#!/usr/bin/env bash
set -euo pipefail

# Research OS — Conda Environment Setup

echo "Setting up Research OS conda environment..."

conda create -n research-os python=3.11 -y
conda activate research-os

pip install --upgrade pip
pip install -r requirements.txt

echo "Environment ready. Activate with: conda activate research-os"
