@echo off
REM Setup virtual environment for Charles Proxy Log Parser MCP

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

echo Virtual environment created and dependencies installed.
echo To activate the virtual environment, run: venv\Scripts\activate.bat 