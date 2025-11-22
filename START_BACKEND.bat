@echo off
echo ========================================
echo Starting Backend Server (Flask)
echo ========================================
echo.

REM Activate virtual environment
call fyp_ml\Scripts\activate.bat

REM Start backend
python backend_server.py

pause
