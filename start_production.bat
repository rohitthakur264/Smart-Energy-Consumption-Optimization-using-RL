@echo off
echo =======================================================
echo     Starting Smart Energy AI Optimizer (Production)
echo =======================================================
echo.
echo Starting FastAPI server on port 8000...
echo The dashboard will be available at: http://localhost:8000/
echo.

call .venv\Scripts\activate.bat
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
