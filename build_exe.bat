@echo off
echo Building CSV Operations EXE...
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
echo Creating EXE file...
pyinstaller --onefile --noconsole --name "CSVOperations" csv_operations.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo.
echo Your EXE file is located at:
echo dist\CSVOperations.exe
echo ========================================
echo.
pause

