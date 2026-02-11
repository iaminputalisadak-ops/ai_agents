@echo off
echo Starting AI Voice Agent (Python 3.12)...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo.
cd /d "%~dp0"
py -3.12 run.py
pause
