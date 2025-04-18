#!/bin/bash

echo "ICMP Events API Deployment Script"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Make the deployment script executable
chmod +x deploy.py
chmod +x check_deployment.py

# Run the deployment script
echo "Running deployment script..."
python3 deploy.py

# Check if deployment was successful
if [ $? -ne 0 ]; then
    echo "Deployment failed. Please check the logs for errors."
    exit 1
fi

# Run the deployment check script
echo
echo "Checking deployment status..."
python3 check_deployment.py

echo
echo "Deployment process completed."
echo "If you encounter any issues, please refer to the DEPLOYMENT.md file." 