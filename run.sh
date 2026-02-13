#!/usr/bin/env bash
# Launch the Flight History Tracker app
cd "$(dirname "$0")"
echo "Installing dependencies..."
pip install -r requirements.txt
python3 app.py
