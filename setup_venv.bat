@echo off
REM Setup virtual environment for Charles Proxy Log Parser MCP

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Create shared directory structure
mkdir ..\mcp-charles-shared\output 2>nul
if not exist ..\mcp-charles-shared\output mkdir ..\mcp-charles-shared\output
echo Created shared directory structure at ..\mcp-charles-shared\output

echo Virtual environment created and dependencies installed.
echo To activate the virtual environment, run: venv\Scripts\activate.bat 