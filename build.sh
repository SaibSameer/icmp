#!/usr/bin/env bash
# Build script for Render deployment

# Exit on error
set -o errexit

# Print each command before executing
set -x

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python init_db.py
cd ..

# Verify installations
echo "Verifying installations..."
pip list | grep jsonschema
pip list | grep psycopg2-binary

# Create necessary directories if they don't exist
echo "Creating necessary directories..."
mkdir -p logs

# Set permissions
echo "Setting permissions..."
chmod -R 755 .

echo "Build completed successfully!" 