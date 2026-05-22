#!/usr/bin/env bash
# Example 02: Data Exploration Workflow

echo "Setting up Data Exploration Environment..."

mkdir -p workspace/data/raw
cp sample.csv workspace/data/raw/

echo "Running Data Exploration Workflow..."
research-os run "Run the 'Peek' protocol on workspace/data/raw/sample.csv. Generate a data profiling report, and then create a 300-DPI scatter plot of interest_rate vs housing_price_index using a viridis color palette."

echo "Workflow complete. Check workspace/figures/ for your plot and workspace/lab_notebook.md for the analysis details."
