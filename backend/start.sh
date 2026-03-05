#!/bin/bash

# Start script for Cloud Image Processing Platform
# This script sets up and starts the Flask backend server

echo "=========================================="
echo "  Cloud Image Processing Platform"
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "✓ Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠ No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created"
fi

# Install/update dependencies
echo ""
echo "Checking dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies ready"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ Warning: .env file not found!"
    echo "  Please copy .env.example to .env and configure it."
    echo ""
    read -p "Do you want to continue with default settings? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the server
echo ""
echo "=========================================="
echo "Starting Flask server..."
echo "=========================================="
echo ""

python app.py