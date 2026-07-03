@echo off
echo Building CSV Operations v1.2.0...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing/Updating PyInstaller...
pip install --upgrade pyinstaller

echo.
echo Creating app folder (--onedir = fast startup, no temp-extract)...

pyinstaller ^
    --onedir ^
    --noconsole ^
    --name "CSVOperations" ^
    --add-data "kblogo.png;." ^
    csv_operations.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo  Build completed successfully!
echo.
echo  App folder : dist\CSVOperations\
echo  Run with  : dist\CSVOperations\CSVOperations.exe
echo.
echo  To distribute: zip the entire dist\CSVOperations\ folder.
echo ================================================
echo.
echo  OPTIONAL: To sign the EXE so Windows shows your name
echo  instead of "Unknown Publisher", run:
echo.
echo    powershell -ExecutionPolicy Bypass -File sign_exe.ps1
echo.
pause
