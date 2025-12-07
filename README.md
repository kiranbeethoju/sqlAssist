# CSV Operations - Desktop Application

A cross-platform desktop application for manipulating and analyzing CSV data. This tool allows you to prepare CSV files, find unique records, identify duplicates, and format data with various delimiters and quote options.

**Available for:** Windows and macOS

## Features

- **CSV Data Input**: Paste or type CSV data directly into the application
- **Flexible Delimiters**: Support for various input and output delimiters (Comma, Semicolon, Pipe, Tab, LF, CR, CRLF)
- **Data Operations**:
  - Prepare CSV: Format and prepare CSV data according to your settings
  - Get Unique: Extract only unique records from your data
  - Get Duplicates: Identify and extract duplicate records
- **Formatting Options**:
  - Ignore enclosed quotes
  - Use single or double quotes
  - Trim data (remove leading/trailing whitespace)
- **Statistics**: View total count, unique records count, and duplicate records count
- **User-Friendly Controls**: Select All, Reset, and Help buttons

## Building Executables

### For macOS

**Quick Build:**
1. Double-click `build_mac.sh` or run in Terminal:
   ```bash
   ./build_mac.sh
   ```
2. Your app will be in `dist/CSVOperations.app`
3. Double-click the app to run it

**Manual Build:**
```bash
pip3 install pyinstaller
pip3 uninstall enum34 -y 2>/dev/null
pyinstaller --onedir --windowed --name "CSVOperations" csv_operations.py
```

The macOS app bundle (`CSVOperations.app`) is located in the `dist` folder and can be run by double-clicking it.

---

### For Windows - Building the EXE File

### Prerequisites

1. **Python 3.8 or higher** installed on your Windows machine
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Verify Python Installation**:
   ```bash
   python --version
   ```

### Step-by-Step Instructions to Create EXE

1. **Open Command Prompt or PowerShell**
   - Press `Win + R`, type `cmd`, and press Enter
   - Or search for "Command Prompt" or "PowerShell" in the Start menu

2. **Navigate to the Project Directory**
   ```bash
   cd "C:\path\to\SqlAssist"
   ```
   (Replace with your actual project path)

3. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```
   Or if you have a requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create the EXE File**
   
   **Option A: Simple One-File EXE (Recommended)**
   ```bash
   pyinstaller --onefile --windowed --name "CSVOperations" csv_operations.py
   ```
   
   **Option B: One-File EXE with Icon (if you have an icon file)**
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico --name "CSVOperations" csv_operations.py
   ```
   
   **Option C: One-File EXE with No Console Window (Clean)**
   ```bash
   pyinstaller --onefile --noconsole --name "CSVOperations" csv_operations.py
   ```

5. **Find Your EXE File**
   - After PyInstaller finishes, navigate to the `dist` folder in your project directory
   - You'll find `CSVOperations.exe` there
   - This is your standalone executable - no installation needed!

6. **Test the EXE**
   - Double-click `CSVOperations.exe` to run it
   - The application should open and work exactly as the Python script

### PyInstaller Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--windowed` or `--noconsole`: Hides the console window (for GUI applications)
- `--name "CSVOperations"`: Sets the name of the output executable
- `--icon=icon.ico`: Adds a custom icon (optional)

### Advanced: Creating a Spec File (Optional)

If you want more control over the build process:

1. **Generate a spec file**:
   ```bash
   pyinstaller --name "CSVOperations" csv_operations.py
   ```

2. **Edit the spec file** (`CSVOperations.spec`) if needed

3. **Build using the spec file**:
   ```bash
   pyinstaller CSVOperations.spec
   ```

### Troubleshooting

**Issue: "pyinstaller is not recognized"**
- Solution: Make sure Python is in your PATH, or use `python -m PyInstaller` instead

**Issue: EXE file is too large**
- Solution: This is normal for PyInstaller. The one-file option bundles Python and all dependencies (~10-20MB)

**Issue: Antivirus flags the EXE**
- Solution: This is a false positive. PyInstaller executables are sometimes flagged. You may need to add an exception or sign the executable

**Issue: EXE doesn't run on another computer**
- Solution: Make sure the target computer has the same Windows architecture (32-bit vs 64-bit). Build for the target architecture:
  ```bash
  pyinstaller --onefile --windowed --name "CSVOperations" csv_operations.py
  ```

### Distribution

The EXE file in the `dist` folder is standalone and can be:
- Copied to any Windows computer
- Run without Python installation
- Shared with others (no installation required)

## Running from Source (Development)

If you want to run the application directly from Python:

```bash
python csv_operations.py
```

## Requirements

- Python 3.8+
- tkinter (included with Python on Windows and macOS)
- PyInstaller (only needed for building executables)

## Usage

1. Launch the application
2. Paste or type your CSV data in the "CSV Data" section
3. Configure your input and output delimiters
4. Select any formatting options you need
5. Click one of the action buttons:
   - **Prepare CSV**: Format your data
   - **Get Unique**: Extract unique records
   - **Get Duplicates**: Find duplicate records
6. View results in the "Output" section
7. Use "Select All" to copy the output, or "Reset" to clear everything

## License

This project is provided as-is for personal and commercial use.

