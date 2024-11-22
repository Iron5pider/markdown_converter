@echo off
call C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat
conda activate markdown_converter
cd C:\projects\markdown_converter
git pull
python app.py
pause
