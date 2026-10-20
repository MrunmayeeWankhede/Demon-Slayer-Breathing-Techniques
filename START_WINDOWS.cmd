@echo off
cd /d "%~dp0"
py -3.11 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.11 launcher.py
  goto done
)
py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  py -3.12 launcher.py
  goto done
)
python -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12)]" >nul 2>nul
if not errorlevel 1 (
  python launcher.py
  goto done
)
echo Install 64-bit Python 3.11 or 3.12 from https://www.python.org/downloads/
echo Include the Python launcher during installation, then open this file again.
pause
exit /b 1
:done
if errorlevel 1 pause
