@echo off
echo ================================================
echo   FTCC04 - Event Simulator
echo ================================================
echo.

REM Get HttpApiUrl from CloudFormation
echo Retrieving HttpApiUrl from deployment...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name ftcc04-serverless-framework --query "Stacks[0].Outputs[?OutputKey=='HttpApiUrl'].OutputValue" --output text 2^>nul') do set HTTP_API_URL=%%i

if "%HTTP_API_URL%"=="" (
    echo ERROR: Could not retrieve HttpApiUrl.
    echo Please ensure the backend is deployed first.
    pause
    exit /b 1
)

echo   HttpApiUrl: %HTTP_API_URL%
echo.

REM Install Python dependencies if needed
echo Checking Python dependencies...
pip install -r "%~dp0backend\requirements.txt" >nul 2>&1
echo   Dependencies ready.
echo.

REM Run the simulator
echo Starting event simulator...
echo Press Ctrl+C to stop.
echo.
python "%~dp0backend\tools\event_source_simulator.py" --url "%HTTP_API_URL%/events" --eps 5 --device device-1

pause
