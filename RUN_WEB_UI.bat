@echo off
chcp 65001 >nul
title SE-Labs — Social Engineering Interactive Web Portal
color 0B

echo =====================================================================
echo   🛡️  SE-Labs: Social Engineering Interactive Web Platform
echo   Cybersecurity Lecture 6 — By : Abdelrahman Hanfy
echo   Ain Shams University
echo =====================================================================
echo.

:: Detect Python environment
set "PY_BIN=python"
if exist "%~dp0..\MethodLab\venv\Scripts\python.exe" (
    set "PY_BIN=%~dp0..\MethodLab\venv\Scripts\python.exe"
)

echo [*] Using Python: %PY_BIN%
echo [*] Starting Web Server on http://127.0.0.1:5500 ...
echo [*] Opening default web browser...
echo.

start "" "http://127.0.0.1:5500"
"%PY_BIN%" "%~dp0app.py"

pause
