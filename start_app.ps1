$env:PYTHONIOENCODING="utf-8"
$env:PYTHONPATH="."

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host 'Starting FastAPI Backend...' -ForegroundColor Cyan; . '\college\SEM 6\NNRL\project 1\.venv\Scripts\Activate.ps1'; python app.py }"

# Start Frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host 'Starting React Frontend...' -ForegroundColor Cyan; cd frontend; npm run dev }"
