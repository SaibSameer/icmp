#!/usr/bin/env python
"""
Run script for the ICMP Events API backend
This script sets up the Python path correctly and runs the app
"""
import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the app
from app import app

if __name__ == "__main__":
    print("Starting ICMP Events API server...")
    app.run(debug=True, host="0.0.0.0", port=5000)