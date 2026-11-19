@echo off
title MedCare Pharmacy Store
echo ==========================================
echo   Starting MedCare Pharmacy E-Commerce
echo ==========================================

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Checking and installing dependencies...
pip install -r requirements.txt

echo Opening browser at http://127.0.0.1:8000/ ...
start "" http://127.0.0.1:8000/

echo Starting Django server (Press Ctrl+C to stop)...
python manage.py runserver
pause