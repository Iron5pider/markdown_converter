@echo off
ECHO Starting Markdown Converter Server...

REM Activate Conda environment
call C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat
conda activate markdown_converter

REM Navigate to project directory
cd C:\projects\markdown_converter

REM Pull latest changes
git pull

REM Start the server
python app.py

ECHO Server is running at http://localhost:5000
pause