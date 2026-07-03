# CSV Operations — Desktop Application · v1.1.0

A cross-platform desktop application for manipulating and analysing CSV data. Paste raw data, format it, extract unique records, identify duplicates, and copy results — all without leaving the app.

**Available for:** Windows and macOS

---

## What's New in v1.1.0

- **App icon** — KB logo (kblogo.png) is now used as the window and dock icon
- **Faster loading** — build scripts switched to `--onedir` mode; the app no longer extracts a temp bundle on every launch, so cold-start time is significantly reduced
- **Always-visible bottom bar** — summary counts and all control buttons are pinned to the bottom of the window and are always visible regardless of window size or scrolling
- **Non-blocking copy confirmation** — "Select All & Copy" now shows a brief green status message in the bottom bar instead of an interruptive popup dialog
- **Send Feedback button** — opens GitHub Issues directly from the app so you can report bugs or request features without leaving the tool
- **Version displayed in title bar and header** — easy to tell which build you are running

---

## Features

- **CSV Data Input** — paste or type CSV data directly into the app
- **Flexible Delimiters** — supports Comma, Semicolon, Pipe, Tab, LF, CR, CRLF for both input and output
- **Data Operations**
  - **Prepare CSV** — format and reformat data with selected delimiter and quote style
  - **Get Unique** — extract only unique records
  - **Get Duplicates** — identify and extract duplicate records
- **Formatting Options**
  - Ignore enclosed quotes
  - Use single or double quotes
  - Trim data (remove leading/trailing whitespace)
- **Live Statistics** — total count, unique records count, duplicate records count always shown in the bottom bar
- **Select All & Copy** — one click to select and copy all output to the clipboard; confirmation appears as a status message (no popup)
- **Send Feedback** — opens GitHub Issues in your browser so you can post bugs or suggestions directly
- **Reset** — clears all data and resets options to defaults
- **Help** — built-in help dialog with usage guide

---

## Building Executables

### macOS

```bash
./build_mac.sh
```

The script will:
1. Install / upgrade PyInstaller
2. Bundle `kblogo.png` with the app
3. Output a double-clickable `dist/CSVOperations.app`

**Manual build:**
```bash
pip3 install pyinstaller
pyinstaller --onedir --windowed --name "CSVOperations" --add-data "kblogo.png:." csv_operations.py
```

---

### Windows

Double-click `build_exe.bat` or run it from a Command Prompt / PowerShell:

```bat
build_exe.bat
```

The script will:
1. Install / upgrade PyInstaller
2. Bundle `kblogo.png` with the app
3. Output a folder at `dist\CSVOperations\`

Run `dist\CSVOperations\CSVOperations.exe` to launch. Zip the entire `dist\CSVOperations\` folder to share with others — no Python installation required.

> **Why `--onedir` instead of `--onefile`?**  
> The `--onefile` format extracts the entire Python runtime to a temp directory on *every launch*, which causes a noticeable delay. `--onedir` skips extraction and starts immediately.

---

## Running from Source (Development)

```bash
python csv_operations.py
```

**Requirements:**
- Python 3.8+
- tkinter (bundled with Python on Windows and macOS)
- PyInstaller (only needed for building executables — `pip install pyinstaller`)

---

## Usage

1. Launch the application
2. Paste or type your CSV data in the **CSV Data** section
3. Configure input and output delimiters
4. Select any formatting options you need
5. Click an action button:
   - **Prepare CSV** — reformat data
   - **Get Unique** — extract unique records
   - **Get Duplicates** — find duplicate records
6. View results in the **Output** section
7. Click **Select All & Copy** to copy to clipboard (status bar confirms — no popup)
8. Use **Reset** to start fresh, or **Send Feedback** to open GitHub Issues

---

## Sending Feedback

Click the **Send Feedback** button inside the app or visit:  
[https://github.com/kiranbeethoju/sqlAssist/issues/new](https://github.com/kiranbeethoju/sqlAssist/issues/new)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pyinstaller` not found | Use `python -m PyInstaller` instead, or add Python's Scripts folder to PATH |
| App doesn't start on another computer | Build on the target OS; macOS apps built on macOS, Windows EXE built on Windows |
| Antivirus flags the EXE | PyInstaller binaries are sometimes flagged as false positives; add an exception or sign the executable |
| Icon not showing on macOS dock | Run the built `.app` from `dist/` rather than the raw Python script |

---

## License

This project is provided as-is for personal and commercial use.
