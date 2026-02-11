@echo off
echo AI Voice Agent - Setup
echo.

cd /d "%~dp0"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Done.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating venv and installing dependencies...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt

if not exist .env (
    echo.
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your OPENAI_API_KEY
    notepad .env
) else (
    echo .env already exists.
)

echo.
echo Setup complete. Run: python run.py
echo Or double-click run.bat
pause
