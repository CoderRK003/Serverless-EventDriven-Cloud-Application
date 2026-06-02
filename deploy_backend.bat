@echo off
echo ================================================
echo   FTCC04 - Deploy Backend Only
echo ================================================
echo.

cd /d "%~dp0infrastructure"

echo Building with SAM...
call sam build
if %errorlevel% neq 0 (
    echo ERROR: SAM build failed.
    pause
    exit /b 1
)
echo.

echo Deploying to AWS...
call sam deploy --guided --stack-name ftcc04-serverless-framework
if %errorlevel% neq 0 (
    echo ERROR: SAM deploy failed.
    pause
    exit /b 1
)
echo.

REM Get outputs
echo ================================================
echo   Deployment Outputs
echo ================================================
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name ftcc04-serverless-framework --query "Stacks[0].Outputs[?OutputKey=='HttpApiUrl'].OutputValue" --output text 2^>nul') do echo   HttpApiUrl: %%i
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name ftcc04-serverless-framework --query "Stacks[0].Outputs[?OutputKey=='WebSocketUrl'].OutputValue" --output text 2^>nul') do echo   WebSocketUrl: %%i
echo ================================================
echo.

pause
