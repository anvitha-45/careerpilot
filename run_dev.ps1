# CareerPilot AI — PowerShell Development Launcher
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "               CareerPilot AI — Starting Full-Stack App" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "Starting React Frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location client; npm.cmd run dev"

Write-Host "`nBoth services launched!" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "- Backend Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

