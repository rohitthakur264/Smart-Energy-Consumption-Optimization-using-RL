$env:PYTHONIOENCODING="utf-8"
$env:PYTHONPATH="."
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting XGBoost CUDA Training" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
. "\college\SEM 6\NNRL\project 1\.venv\Scripts\Activate.ps1"
python train_model_cuda.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting RL Models Training on CUDA" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
python train_agent_v2.py --mode both

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  All Training Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Press any key to close this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
