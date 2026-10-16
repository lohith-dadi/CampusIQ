@echo off
setlocal enabledelayedexpansion

title CampusIQ - Smart Campus Space Intelligence

echo ==============================================================================
echo        CAMPUSIQ -- SMART CAMPUS SPACE INTELLIGENCE (DATATHON 2026)
echo ==============================================================================
echo.

:: 1. Change to the directory of this batch file
cd /d "%~dp0"
echo [OK] Working Directory: %CD%

:: 2. Detect Python
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3.13"
    %PY_CMD% --version >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        set "PY_CMD=py"
    )
    goto :PYTHON_FOUND
)

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_FOUND
)

echo [ERROR] Python was not found in your system PATH.
echo Please install Python 3.10+ from https://www.python.org/ or the Microsoft Store.
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [OK] Using Python: %PY_CMD%
%PY_CMD% --version

:: 3. Launch Streamlit Application
echo.
echo [STARTING] Launching CampusIQ Streamlit Dashboard on http://localhost:8501 ...
%PY_CMD% -m streamlit run app.py --server.port 8501

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Streamlit encountered an issue while running.
    echo If dependencies are missing, run: %PY_CMD% -m pip install -r requirements.txt
    echo.
    pause
)
