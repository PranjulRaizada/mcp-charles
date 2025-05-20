#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dashboard dependencies..."
pip install -r dashboard_requirements.txt

# Run the dashboard
echo "Starting dashboard..."
streamlit run dashboard.py 