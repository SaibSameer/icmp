#!/usr/bin/env python
"""
Script to check CORS headers on API endpoints.
"""

import requests
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def check_cors(base_url='http://127.0.0.1:5000'):
    """Check CORS headers for various endpoints"""
    
    # Define endpoints to test
    endpoints = [
        '/api/message',
        '/api/message/logs/recent',
        '/health',
        '/ping'
    ]
    
    # Test each endpoint with an OPTIONS request
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        log.info(f"Testing OPTIONS request for {url}")
        
        try:
            # Use OPTIONS method for preflight request
            response = requests.options(
                url,
                headers={
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type, Authorization'
                }
            )
            
            # Check response status code
            log.info(f"Status code: {response.status_code}")
            
            # Print headers
            log.info("Response headers:")
            for key, value in response.headers.items():
                if key.lower().startswith('access-control'):
                    log.info(f"  {key}: {value}")
            
            # Check if key CORS headers are present
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            missing_headers = [h for h in cors_headers if h not in response.headers]
            if missing_headers:
                log.error(f"Missing CORS headers: {missing_headers}")
            else:
                log.info(f"All required CORS headers present for {endpoint}")
                
            log.info("-" * 80)
            
        except requests.exceptions.RequestException as e:
            log.error(f"Error testing {url}: {e}")
            log.info("-" * 80)

if __name__ == "__main__":
    # Use custom base URL if provided as command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5000'
    check_cors(base_url)