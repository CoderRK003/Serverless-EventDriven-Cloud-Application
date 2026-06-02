@echo off
echo ================================================
echo   FTCC04 - Run Frontend Only
echo ================================================
echo.

cd /d "%~dp0frontend"

REM Check if .env exists
if not exist "%~dp0frontend\.env" (
    echo WARNING: .env file not found!
    echo.
    echo To configure .env, run run_project.bat or deploy_backend.bat first.
    echo.
    echo Creating .env with placeholder values...
    echo VITE_HTTP_API_BASE=https://your-api.execute-api.region.amazonaws.com> .env
    echo VITE_WS_URL=wss://your-api.execute-api.region.amazonaws.com/dev>> .env
    echo.
    echo Please edit the .env file with your actual values.
    echo.
    pause
    exit /b 1
)

echo Starting frontend development server...
echo Open: http://localhost:5173
echo Press Ctrl+C to stop.
echo.

npm run dev
