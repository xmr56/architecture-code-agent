@echo off
cd /d "%~dp0"
python bootstrap_runtime.py
if errorlevel 1 goto failed
python app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Startup failed. Check Python installation and network.
pause
exit /b 1
