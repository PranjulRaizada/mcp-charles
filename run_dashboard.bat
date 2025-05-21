@echo off
:: This script runs the streamlit dashboard for visualizing Charles logs

:: Determine script directory
pushd %~dp0

:: Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating one...
    call setup_venv.bat
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run dashboard
echo Starting dashboard...
streamlit run dashboard\dashboard.py

:: Deactivate at end
call deactivate

:: Return to original directory
popd 