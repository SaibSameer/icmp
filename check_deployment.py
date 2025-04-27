#!/usr/bin/env python
# check_deployment.py - Script to check deployment status

import os
import sys
import requests
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv('REACT_APP_API_URL', 'https://icmp-api.onrender.com')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://icmp.onrender.com')
FB_VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN')
FB_PAGE_ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')

def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            log.info(f"API health check passed: {response.json()}")
            return True
        else:
            log.error(f"API health check failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log.error(f"Error checking API health: {str(e)}")
        return False

def check_facebook_integration():
    """Check if Facebook integration is configured"""
    if not FB_VERIFY_TOKEN:
        log.error("FB_VERIFY_TOKEN is not set")
        return False
    
    if not FB_PAGE_ACCESS_TOKEN:
        log.error("FB_PAGE_ACCESS_TOKEN is not set")
        return False
    
    log.info("Facebook integration tokens are set")
    return True

def check_database_connection():
    """Check if the database connection is working"""
    try:
        from backend.db import get_db_connection, release_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        release_db_connection(conn)
        
        if result and result[0] == 1:
            log.info("Database connection is working")
            return True
        else:
            log.error("Database connection test failed")
            return False
    except Exception as e:
        log.error(f"Error checking database connection: {str(e)}")
        return False

def check_frontend_connection():
    """Check if the frontend can connect to the API"""
    try:
        response = requests.get(f"{FRONTEND_URL}")
        if response.status_code == 200:
            log.info(f"Frontend is accessible: {FRONTEND_URL}")
            return True
        else:
            log.error(f"Frontend is not accessible with status code {response.status_code}")
            return False
    except Exception as e:
        log.error(f"Error checking frontend: {str(e)}")
        return False

def main():
    """Main function to run all checks"""
    log.info("Starting deployment checks...")
    
    api_health = check_api_health()
    facebook_integration = check_facebook_integration()
    database_connection = check_database_connection()
    frontend_connection = check_frontend_connection()
    
    log.info("Deployment check results:")
    log.info(f"API Health: {'✅' if api_health else '❌'}")
    log.info(f"Facebook Integration: {'✅' if facebook_integration else '❌'}")
    log.info(f"Database Connection: {'✅' if database_connection else '❌'}")
    log.info(f"Frontend Connection: {'✅' if frontend_connection else '❌'}")
    
    if all([api_health, facebook_integration, database_connection, frontend_connection]):
        log.info("All checks passed! Deployment is working correctly.")
        return 0
    else:
        log.error("Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 