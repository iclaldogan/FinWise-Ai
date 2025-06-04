#!/bin/bash

# FinWise AI Setup Script
# This script sets up a virtual environment and installs dependencies

echo "Setting up FinWise AI application..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! Run the following commands to start the server:"
echo "source venv/bin/activate"
echo "cd finwise_ai"
echo "python manage.py runserver"
echo ""
echo "Then visit http://127.0.0.1:8000/ in your browser"
echo ""
echo "Demo account:"
echo "Email: demo@finwiseai.com"
echo "Password: demopassword"
