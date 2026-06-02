@echo off
echo ================================================
echo   FTCC04 - Serverless Event-Driven Framework
echo ================================================
echo.

REM Check prerequisites
echo [1/6] Checking prerequisites...
where sam >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS SAM CLI not found. Please install it first.
    echo Download: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+ first.
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo   All prerequisites found.
echo.

REM Step 1: Build and Deploy Backend
echo [2/6] Building backend with AWS SAM...
cd /d "%~dp0infrastructure"
call sam build
if %errorlevel% neq 0 (
    echo ERROR: SAM build failed.
    pause
    exit /b 1
)
echo.

echo [3/6] Deploying backend to AWS...
echo   This will prompt for configuration on first run.
echo   Press Enter to continue or Ctrl+C to cancel...
pause

call sam deploy --guided --stack-name ftcc04-serverless-framework
if %errorlevel% neq 0 (
    echo ERROR: SAM deploy failed.
    pause
    exit /b 1
)
echo.

REM Step 2: Get outputs from CloudFormation
echo [4/6] Retrieving deployment outputs...
cd /d "%~dp0infrastructure"

REM Get HttpApiUrl
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name ftcc04-serverless-framework --query "Stacks[0].Outputs[?OutputKey=='HttpApiUrl'].OutputValue" --output text 2^>nul') do set HTTP_API_URL=%%i

REM Get WebSocketUrl
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name ftcc04-serverless-framework --query "Stacks[0].Outputs[?OutputKey=='WebSocketUrl'].OutputValue" --output text 2^>nul') do set WS_URL=%%i

if "%HTTP_API_URL%"=="" (
    echo ERROR: Could not retrieve HttpApiUrl. Please check deployment.
    pause
    exit /b 1
)

if "%WS_URL%"=="" (
    echo ERROR: Could not retrieve WebSocketUrl. Please check deployment.
    pause
    exit /b 1
)

echo   HttpApiUrl: %HTTP_API_URL%
echo   WebSocketUrl: %WS_URL%
echo.

REM Step 3: Configure frontend
echo [5/6] Configuring frontend environment...
cd /d "%~dp0frontend"

echo VITE_HTTP_API_BASE=%HTTP_API_URL%> .env
echo VITE_WS_URL=%WS_URL%>> .env
echo.

REM Step 4: Install frontend dependencies
echo [6/6] Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: npm install failed.
    pause
    exit /b 1
)
echo.

REM Step 5: Run frontend
echo ================================================
echo   Deployment Complete!
echo ================================================
echo.
echo   HttpApiUrl: %HTTP_API_URL%
echo   WebSocketUrl: %WS_URL%
echo.
echo   Starting frontend development server...
echo   Open: http://localhost:5173
echo.
echo   Press Ctrl+C to stop the server.
echo ================================================
echo.

cd /d "%~dp0frontend"
npm run dev
