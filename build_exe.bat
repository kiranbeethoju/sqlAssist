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
REM --onedir  : folder-based build - starts MUCH faster than --onefile
REM             because it doesn't need to extract to a temp folder on every launch
REM --add-data: bundles kblogo.png so the icon is available inside the build
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
echo ========================================
echo Build completed successfully!
echo.
echo Your app folder is located at:
echo dist\CSVOperations\
echo.
echo Run dist\CSVOperations\CSVOperations.exe to launch.
echo (You can zip the entire dist\CSVOperations\ folder for distribution.)
echo ========================================
echo.
pause
