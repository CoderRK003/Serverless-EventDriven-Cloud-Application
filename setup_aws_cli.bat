@echo off
echo ================================================
echo   AWS CLI Configuration
echo ================================================
echo.
echo Open your rootkey.csv file and copy the values.
echo.

set /p ACCESS_KEY="Enter AWSAccessKeyId: "
set /p SECRET_KEY="Enter AWSSecretKey: "

set AWS_CONFIG_FILE=%USERPROFILE%\.aws\config
set AWS_CREDS_FILE=%USERPROFILE%\.aws\credentials

if not exist "%USERPROFILE%\.aws" mkdir "%USERPROFILE%\.aws"

echo [default] > "%AWS_CREDS_FILE%"
echo aws_access_key_id = %ACCESS_KEY% >> "%AWS_CREDS_FILE%"
echo aws_secret_access_key = %SECRET_KEY% >> "%AWS_CREDS_FILE%"

echo. > "%AWS_CONFIG_FILE%"
echo [default] >> "%AWS_CONFIG_FILE%"
echo region = ap-south-1 >> "%AWS_CONFIG_FILE%"
echo output = json >> "%AWS_CONFIG_FILE%"

echo.
echo ================================================
echo   AWS CLI Configured Successfully!
echo ================================================
echo.

echo Verifying credentials...
aws sts get-caller-identity

echo.
pause
