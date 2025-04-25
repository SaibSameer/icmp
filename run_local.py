#!/usr/bin/env python3
"""
Script to run the application locally with the correct environment settings.
This bypasses the Render-specific configuration in application.py.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env files
backend_env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path)
    print(f"Loaded environment from {backend_env_path}")
else:
    print(f"Warning: {backend_env_path} not found")

# Ensure the backend directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import directly from backend.app to bypass application.py
try:
    from backend.app import app

    if __name__ == '__main__':
        print("Starting local development server...")
        print(f"Database: {os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}")
        print(f"User: {os.environ.get('DB_USER')}")
        app.run(host='0.0.0.0', port=5000, debug=True)
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1) 