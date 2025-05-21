#!/bin/bash

# This script runs the streamlit dashboard for visualizing Charles logs

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    ./setup_venv.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run dashboard
streamlit run dashboard/dashboard.py

# Deactivate at end
deactivate 