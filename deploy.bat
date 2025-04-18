@echo off
echo ICMP Events API Deployment Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    exit /b 1
)

REM Run the deployment script
echo Running deployment script...
python deploy.py

REM Check if deployment was successful
if %errorlevel% neq 0 (
    echo Deployment failed. Please check the logs for errors.
    exit /b 1
)

REM Run the deployment check script
echo.
echo Checking deployment status...
python check_deployment.py

echo.
echo Deployment process completed.
echo If you encounter any issues, please refer to the DEPLOYMENT.md file. 