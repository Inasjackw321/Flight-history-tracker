@echo off
cd /d "%~dp0"

echo === Flight History Tracker ===
echo.

echo Installing dependencies...
py -3 -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo pip failed, trying with python...
    python -m pip install -r requirements.txt
)

echo.
echo Starting app...
py -3 app.py
if %errorlevel% neq 0 (
    echo py launcher not found, trying python...
    python app.py
)

echo.
pause
