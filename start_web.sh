#!/bin/bash

# Start script for Trailer-to-Campaign Autopilot Web UI
# This script ensures Flask is installed and starts the web server

echo "🎬 Starting Trailer-to-Campaign Autopilot Web UI..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected."
    echo "If you have a venv, activate it first:"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Flask if not already installed
echo "📦 Checking Flask installation..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Flask..."
    pip install flask
else
    echo "✅ Flask is already installed"
fi

echo ""
echo "🚀 Starting web server on http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

# Start the Flask app
python3 web/app.py
