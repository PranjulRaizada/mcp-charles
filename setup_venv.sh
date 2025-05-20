#!/bin/bash
# Setup virtual environment for Charles Proxy Log Parser MCP

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Virtual environment created and dependencies installed."
echo "To activate the virtual environment, run: source venv/bin/activate" 