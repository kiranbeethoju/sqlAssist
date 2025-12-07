# How to Build Windows EXE - Step by Step Guide

## ⚠️ Important Note
**You must build the EXE on a Windows computer.** PyInstaller creates executables for the platform it runs on, so you cannot create a Windows EXE on macOS or Linux.

## Quick Build Instructions

### Option 1: Use the Batch Script (Easiest)

1. **Copy the project folder to a Windows computer**
2. **Double-click `build_exe.bat`**
3. **Wait for the build to complete**
4. **Find your EXE in the `dist` folder: `CSVOperations.exe`**

### Option 2: Manual Build via Command Prompt

1. **Open Command Prompt** (Press `Win + R`, type `cmd`, press Enter)

2. **Navigate to the project folder:**
   ```cmd
   cd C:\path\to\SqlAssist
   ```

3. **Install PyInstaller:**
   ```cmd
   pip install pyinstaller
   ```

4. **Build the EXE:**
   ```cmd
   pyinstaller --onefile --noconsole --name "CSVOperations" csv_operations.py
   ```

5. **Your EXE is ready!**
   - Location: `dist\CSVOperations.exe`
   - Size: Approximately 10-15 MB
   - No installation needed - just double-click to run!

## Detailed Build Command Options

### Basic Build (Single File, No Console)
```cmd
pyinstaller --onefile --noconsole --name "CSVOperations" csv_operations.py
```

### Build with Custom Icon (if you have icon.ico)
```cmd
pyinstaller --onefile --noconsole --icon=icon.ico --name "CSVOperations" csv_operations.py
```

### Build with Console Window (for debugging)
```cmd
pyinstaller --onefile --name "CSVOperations" csv_operations.py
```

## What Gets Created

After building, you'll see:
- **`build/`** folder - Temporary build files (can be deleted)
- **`dist/`** folder - **Contains your EXE file!**
- **`CSVOperations.spec`** - Build configuration (can be kept for future builds)

## Testing the EXE

1. Navigate to the `dist` folder
2. Double-click `CSVOperations.exe`
3. The application should open immediately
4. Test with sample CSV data to verify it works

## Troubleshooting

### "Python is not recognized"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart Command Prompt after installation

### "pip is not recognized"
- Use `python -m pip install pyinstaller` instead
- Or reinstall Python with "Add to PATH" option

### EXE is flagged by antivirus
- This is a false positive common with PyInstaller
- Add an exception in your antivirus software
- Or use Windows Defender exclusion

### EXE doesn't run on another computer
- Make sure both computers are the same architecture (32-bit or 64-bit)
- The EXE should work on Windows 7, 8, 10, and 11

## File Structure After Build

```
SqlAssist/
├── csv_operations.py          (source code)
├── build_exe.bat              (build script)
├── requirements.txt           (dependencies)
├── README.md                  (documentation)
├── BUILD_WINDOWS_EXE.md       (this file)
├── build/                     (temporary - can delete)
│   └── CSVOperations/
├── dist/                      (YOUR EXE IS HERE!)
│   └── CSVOperations.exe      ⭐ This is what you need!
└── CSVOperations.spec         (build config - optional)
```

## Distribution

The `CSVOperations.exe` file is completely standalone:
- ✅ No Python installation required
- ✅ No dependencies needed
- ✅ Works on any Windows computer
- ✅ Just copy and run!

You can share this single EXE file with anyone, and it will work on their Windows computer without any setup.

