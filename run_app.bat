@echo off
cd /d "%~dp0"

echo [1/3] Checking virtual environment...
if not exist ".venv" (
    echo Creating new virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/3] Installing/verifying dependencies...
pip install -r requirements.txt

echo.
echo ========================================================
echo Environment is ready! Starting the application...
echo ========================================================
echo.

python quick_start.py
pause
