@echo off
chcp 65001 >nul
title Social Engineering Labs — Launcher
color 0A

:: Detect Python environment
set "PY_BIN=python"
if exist "%~dp0..\MethodLab\venv\Scripts\python.exe" (
    set "PY_BIN=%~dp0..\MethodLab\venv\Scripts\python.exe"
)

:menu
cls
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   Social Engineering Practical Labs — Lecture 6 Launcher         ║
echo ║   By : Abdelrahman Hanfy — Ain Shams University                 ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo   ⭐ [W] LAUNCH MODERN WEB UI PLATFORM (Recommended - http://127.0.0.1:5500)
echo.
echo   --- Terminal / CLI Simulation Labs ---
echo   [1] Lab 1A: Email Header Forensic Analyzer (all 6 samples)
echo   [2] Lab 1B: Phishing Credential Harvesting Page (localhost:8080)
echo   [3] Lab 2A: Typosquatting Domain Generator
echo   [4] Lab 2B: Open Redirect Vulnerability Simulator
echo   [5] Lab 3:  Pharming Attack Simulator (Hosts + DNS)
echo   [6] Lab 4A: USB Baiting Canary Token Demo
echo   [7] Lab 4B: Disinformation / Hoax Detection Quiz
echo   [8] Lab 5:  Pretexting, OSINT ^& Dumpster Diving
echo   [9] Lab 6:  Watering Hole Attack (Source Diff)
echo   [A] Lab 7:  Physical SE Awareness Quiz
echo   [B] Lab 8:  SOC Defense Dashboard (Capstone)
echo   [Q] Quit
echo.
set /p choice="  Select an option: "

if /i "%choice%"=="w" goto webui
if /i "%choice%"=="1" goto lab1a
if /i "%choice%"=="2" goto lab1b
if /i "%choice%"=="3" goto lab2a
if /i "%choice%"=="4" goto lab2b
if /i "%choice%"=="5" goto lab3
if /i "%choice%"=="6" goto lab4a
if /i "%choice%"=="7" goto lab4b
if /i "%choice%"=="8" goto lab5
if /i "%choice%"=="9" goto lab6
if /i "%choice%"=="a" goto lab7
if /i "%choice%"=="b" goto lab8
if /i "%choice%"=="q" exit
goto menu

:webui
cls
echo === Launching Modern Web UI on http://127.0.0.1:5500 ===
echo.
start "" "http://127.0.0.1:5500"
"%PY_BIN%" "%~dp0app.py"
pause
goto menu

:lab1a
cls
echo === Lab 1A: Email Header Forensic Analyzer ===
echo.
cd /d "%~dp0lab1-phishing"
"%PY_BIN%" header_analyzer.py --all
echo.
pause
goto menu

:lab1b
cls
echo === Lab 1B: Phishing Server (open http://127.0.0.1:8080) ===
echo.
cd /d "%~dp0lab1-phishing"
start "" http://127.0.0.1:8080
"%PY_BIN%" phishing_server.py
pause
goto menu

:lab2a
cls
echo === Lab 2A: Typosquatting Generator ===
set /p domain="  Enter domain to analyze (e.g., amazon.com): "
echo.
cd /d "%~dp0lab2-redirection"
"%PY_BIN%" typosquatting_generator.py %domain%
echo.
pause
goto menu

:lab2b
cls
echo === Lab 2B: Open Redirect Simulator ===
echo   Safe:      http://127.0.0.1:8081/login
echo   Malicious: http://127.0.0.1:8081/login?redirect=http://127.0.0.1:9090/evil
echo.
cd /d "%~dp0lab2-redirection"
start "" http://127.0.0.1:8081/login
"%PY_BIN%" open_redirect_simulator.py
pause
goto menu

:lab3
cls
echo === Lab 3: Pharming Simulator ===
echo   Real Bank:      http://127.0.0.1:8082
echo   Attacker Clone: http://127.0.0.1:9091
echo.
cd /d "%~dp0lab3-pharming"
start "" http://127.0.0.1:8082
timeout /t 1 >nul
start "" http://127.0.0.1:9091
"%PY_BIN%" pharming_simulator.py
pause
goto menu

:lab4a
cls
echo === Lab 4A: USB Baiting Canary Token Demo ===
echo.
cd /d "%~dp0lab4-baiting-disinfo"
"%PY_BIN%" canary_usb_simulator.py --demo
pause
goto menu

:lab4b
cls
echo === Lab 4B: Disinformation / Hoax Quiz ===
echo.
cd /d "%~dp0lab4-baiting-disinfo"
"%PY_BIN%" hoax_detector.py
pause
goto menu

:lab5
cls
echo === Lab 5: Pretexting, OSINT ^& Dumpster Diving ===
echo.
cd /d "%~dp0lab5-pretexting-osint"
"%PY_BIN%" pretexting_osint_lab.py
pause
goto menu

:lab6
cls
echo === Lab 6: Watering Hole Attack ===
echo   Clean:       http://127.0.0.1:8083
echo   Compromised: http://127.0.0.1:8084
echo.
cd /d "%~dp0lab6-watering-hole"
start "" http://127.0.0.1:8083
timeout /t 1 >nul
start "" http://127.0.0.1:8084
"%PY_BIN%" watering_hole_simulator.py
pause
goto menu

:lab7
cls
echo === Lab 7: Physical SE Awareness Quiz ===
echo.
cd /d "%~dp0lab7-physical-se"
"%PY_BIN%" physical_se_quiz.py
pause
goto menu

:lab8
cls
echo === Lab 8: SOC Defense Dashboard (Capstone) ===
echo.
cd /d "%~dp0lab8-defense"
"%PY_BIN%" defense_dashboard.py
pause
goto menu
