#!/bin/bash
set -e

echo "Starting daily scraper script..."
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"

source /app/venv/bin/activate
echo "Activated virtual environment"
echo "Python path after venv: $(which python)"

export LD_LIBRARY_PATH=$(dirname $(find /nix/store -name libstdc++.so.6 2>/dev/null | head -1)):$LD_LIBRARY_PATH
echo "Set LD_LIBRARY_PATH: $LD_LIBRARY_PATH"

echo "Running scraper..."
python -m app.fbref_scraper.main_scraper --mode daily --days 2

echo "Scraper completed successfully"
