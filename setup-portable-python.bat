@echo off
echo ========================================
echo Portable Python Setup for CSV Operations
echo ========================================
echo.

REM Check if portable Python exists
if not exist "PortablePython\python.exe" (
    echo ERROR: Portable Python not found!
    echo.
    echo Please download Python embeddable package:
    echo 1. Go to: https://www.python.org/downloads/windows/
    echo 2. Download "Windows embeddable package (64-bit)" - ZIP file
    echo 3. Extract it to: PortablePython folder in this directory
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Found Portable Python!
echo.

REM Install pip if not present
if not exist "PortablePython\Scripts\pip.exe" (
    echo Installing pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    PortablePython\python.exe get-pip.py
    del get-pip.py
)

echo Installing PyInstaller...
PortablePython\python.exe -m pip install pyinstaller

echo.
echo ========================================
echo Building EXE...
echo ========================================
echo.

PortablePython\python.exe -m PyInstaller --onefile --noconsole --name "CSVOperations" csv_operations.py

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

