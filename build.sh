#!/usr/bin/env bash
# Build script for Render deployment

# Exit on error
set -o errexit

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Create necessary directories if they don't exist
echo "Creating necessary directories..."
mkdir -p logs

# Set permissions
echo "Setting permissions..."
chmod -R 755 .

echo "Build completed successfully!" 