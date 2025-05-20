@echo off
echo Charles Log Dashboard Launcher

REM Check if virtual environment exists
if exist venv\ (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo Installing dashboard dependencies...
pip install -r dashboard_requirements.txt

REM Run the dashboard
echo Starting dashboard...
streamlit run dashboard.py

pause 