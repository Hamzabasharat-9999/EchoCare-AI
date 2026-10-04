@echo off
setlocal
cd /d "%~dp0"

echo.
echo ================================================
echo          EchoCare AI ^| Premium Clinical Copilot
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo.
    echo ERROR: Could not create the virtual environment.
    pause
    exit /b 1
  )
) else (
  echo [1/3] Virtual environment already exists.
)

call ".venv\Scripts\activate.bat"

echo [2/3] Checking dependencies...
pip install -r requirements.txt --timeout 300 --retries 10 --disable-pip-version-check
if errorlevel 1 (
  echo.
  echo ERROR: Dependency installation failed.
  echo This is usually a network timeout. Run this file again; pip will reuse cached packages.
  echo.
  pause
  exit /b 1
)

echo [3/3] Launching EchoCare AI...
echo.
streamlit run app.py

endlocal
