#!/usr/bin/env python
# check_deployment.py - Script to check if the deployment was successful

import requests
import sys
import time
import os
from dotenv import load_dotenv

def check_health_endpoint():
    """Check if the health endpoint is responding."""
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Health endpoint is responding correctly.")
            return True
        else:
            print(f"❌ Health endpoint returned status code {response.status_code}.")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Is it running?")
        return False

def check_database_connection():
    """Check if the database connection is working."""
    try:
        response = requests.get("http://localhost:5000/ping")
        if response.status_code == 200:
            print("✅ Database connection is working.")
            return True
        else:
            print(f"❌ Database connection check returned status code {response.status_code}.")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Is it running?")
        return False

def main():
    """Main function to check the deployment."""
    print("Checking deployment status...")
    
    # Wait for the application to start
    print("Waiting for the application to start (30 seconds)...")
    time.sleep(30)
    
    # Check health endpoint
    health_ok = check_health_endpoint()
    
    # Check database connection
    db_ok = check_database_connection()
    
    # Print summary
    if health_ok and db_ok:
        print("\n✅ Deployment successful! The application is running correctly.")
        return 0
    else:
        print("\n❌ Deployment check failed. Please check the logs for errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 