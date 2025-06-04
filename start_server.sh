#!/bin/bash

# FinWise AI Startup Script
# This script activates the virtual environment and starts the Django server

echo "Starting FinWise AI application..."
echo "Activating virtual environment..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Change to the project directory
cd "$SCRIPT_DIR/finwise_ai"

# Start the Django development server
echo "Starting Django server on http://127.0.0.1:8000/"
echo "Use Ctrl+C to stop the server"
python manage.py runserver

# Deactivate the virtual environment when the server stops
deactivate
