#!/bin/bash

echo "Building CSV Operations for macOS..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

echo "Installing/Updating PyInstaller..."
pip3 install --upgrade pyinstaller

# Remove enum34 if it exists (incompatible with PyInstaller)
pip3 uninstall enum34 -y 2>/dev/null

echo ""
echo "Creating macOS app bundle..."

# Clean previous builds
rm -rf build dist CSVOperations.spec

# Build the app
pyinstaller --onedir --windowed --name "CSVOperations" csv_operations.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Build completed successfully!"
    echo ""
    echo "Your macOS app is located at:"
    echo "dist/CSVOperations.app"
    echo ""
    echo "To run it, double-click CSVOperations.app"
    echo "or run: open dist/CSVOperations.app"
    echo "========================================"
else
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

