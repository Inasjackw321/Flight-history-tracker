#!/usr/bin/env bash
# Launch the Flight History Tracker app
cd "$(dirname "$0")"
pip install -q -r requirements.txt 2>/dev/null
python3 app.py
