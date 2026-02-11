@echo off
cd /d "%~dp0"
echo Starting AI Voice Agent...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo.
py -3.12 run.py
if errorlevel 1 (
    echo.
    echo ERROR: Run failed. Make sure Python 3.12 is installed.
    echo Run: py -3.12 -m pip install -r backend\requirements.txt
)
pause
