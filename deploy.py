#!/usr/bin/env python
# deploy.py - Script to deploy the ICMP Events API

import os
import sys
import subprocess
import platform
import venv
import shutil
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
    else:
        print("Virtual environment already exists.")

def get_python_executable():
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def get_pip_executable():
    """Get the path to the pip executable in the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "pip.exe")
    else:
        return os.path.join("venv", "bin", "pip")

def install_dependencies():
    """Install the required dependencies."""
    print("Installing dependencies...")
    pip_executable = get_pip_executable()
    subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
    subprocess.run([pip_executable, "install", "-r", "backend/requirements.txt"], check=True)

def setup_environment():
    """Set up the environment variables."""
    print("Setting up environment variables...")
    # Check if .env file exists, if not create it
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""DB_NAME=icmp_db
DB_USER=icmp_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
POSTGRES_PASSWORD=postgres""")
        print("Created .env file with default values. Please update with your actual database credentials.")

def run_application():
    """Run the application."""
    print("Starting the application...")
    python_executable = get_python_executable()
    subprocess.run([python_executable, "application.py"], check=True)

def main():
    """Main function to deploy the application."""
    try:
        create_virtual_environment()
        install_dependencies()
        setup_environment()
        run_application()
    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()