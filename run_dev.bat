@echo off
echo ======================================================================
echo                CareerPilot AI — Starting Full-Stack App
echo ======================================================================
echo.

echo Starting FastAPI Backend on http://localhost:8000 ...
start "CareerPilot Backend" cmd /k "python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting React Vite Frontend on http://localhost:5173 ...
cd client
start "CareerPilot Frontend" cmd /k "npm.cmd run dev"

echo.
echo Both services launched!
echo - Frontend: http://localhost:5173
echo - Backend API Docs: http://localhost:8000/docs
echo ======================================================================
pause

