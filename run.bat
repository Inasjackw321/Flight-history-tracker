@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt
python app.py
pause
