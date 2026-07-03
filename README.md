# CSV Operations — Desktop Application · v1.2.0

A cross-platform desktop application for manipulating CSV data **and building SQL queries**.  
Paste raw data, format it, extract unique records, identify duplicates, generate CRUD SQL, and save frequently-used queries — all offline, no browser needed.

**Available for:** Windows and macOS

---

## What's New in v1.2.0

| Feature | Details |
|---|---|
| **SQL Builder tab** | Pick any configured database, table, and columns → generate SELECT / INSERT / UPDATE / DELETE queries with one click |
| **Saved Queries tab** | Save named queries, copy them with one click, rename or delete — all persisted to disk |
| **DB Config tab** | Add/edit/delete databases, tables and columns; bulk-paste columns comma-separated |
| **Capitalize All** | One-click UPPERCASE conversion of all input data |
| **Font zoom** | Ctrl + scroll wheel or Ctrl +/− or the +/− buttons in the bottom bar |
| **Offline badge** | Header clearly shows this is an offline app — no internet required |
| **Default single-quotes & trim** | "Use single quotes" and "Trim data" are on by default |
| **Persistent preferences** | Font size, delimiter choices, and options are saved between sessions |
| **Windows code signing** | `sign_exe.ps1` script to sign the EXE so Windows shows "Kiran Beethoju" instead of "Unknown Publisher" |

---

## What's New in v1.1.0

- KB logo as window/dock icon and header thumbnail
- Faster loading — `--onedir` PyInstaller build (no temp-extract on launch)
- Always-visible bottom bar with summary counts and buttons
- Non-blocking copy toast (no popup dialog)
- Send Feedback button → GitHub Issues
- Version in title bar and header

---

## Features

### CSV Operations Tab
- Paste or type CSV data
- Choose input / output delimiters (Comma, Semicolon, Pipe, Tab, LF, CR, CRLF)
- **Prepare CSV** — reformat with selected delimiter and quote style
- **Get Unique** — extract unique records
- **Get Duplicates** — identify duplicate records
- **Capitalize All** — convert all values to UPPERCASE instantly
- Formatting options: ignore enclosed quotes, single/double quotes, trim whitespace

### SQL Builder Tab
- Select configured database → table → columns (with checkboxes)
- Add a WHERE clause
- Generate **SELECT**, **INSERT**, **UPDATE**, **DELETE** queries
- Copy SQL or save it to your query library

### Saved Queries Tab
- Browse all saved queries with a preview
- One-click copy to clipboard
- Double-click to load into SQL Builder
- Rename or delete any entry

### DB Config Tab
- Add / rename / delete databases and tables
- Add columns one by one or bulk-paste a comma-separated list
- All config persisted to `~/.csvoperations/config.json`

### Bottom Bar (always visible)
- Live summary: Total · Unique · Duplicates counts
- Font size controls (+ / − buttons or Ctrl+scroll)
- **Select All & Copy** — copies output (status toast, no popup)
- **Reset**, **Send Feedback**, **Help**

---

## Building Executables

### macOS

```bash
./build_mac.sh
```

Output: `dist/CSVOperations.app` — double-click to run.

**Manual:**
```bash
pip3 install pyinstaller
pyinstaller --onedir --windowed --name "CSVOperations" --add-data "kblogo.png:." csv_operations.py
```

---

### Windows

```bat
build_exe.bat
```

Output: `dist\CSVOperations\` folder — run `dist\CSVOperations\CSVOperations.exe`.

Zip the entire `dist\CSVOperations\` folder to share with others — no Python required.

#### Optional: Fix "Unknown Publisher" warning

Run `sign_exe.ps1` after building:

```powershell
powershell -ExecutionPolicy Bypass -File sign_exe.ps1
```

This creates a **self-signed certificate** (stored as `KiranB_CodeSign.pfx`) and signs the EXE so Windows shows **"Kiran Beethoju"** as the publisher instead of "Unknown Publisher".

> **Note:** A self-signed certificate removes the "Unknown Publisher" label.  
> For zero SmartScreen warnings on first run, you need an **EV code-signing certificate**  
> from [DigiCert](https://www.digicert.com/signing/code-signing-certificates) or [Sectigo](https://sectigo.com/ssl-certificates-tls/code-signing) (~$300–500/yr).

---

## Running from Source

```bash
python csv_operations.py
```

**Requirements:**
- Python 3.8+
- tkinter (bundled with Python on Windows and macOS)
- No other dependencies — pure standard library

Config is stored at `~/.csvoperations/config.json` (created automatically on first run).

---

## Usage

1. **CSV Operations** — paste data, configure options, click an action button, copy the output
2. **DB Config** — add your databases and tables with their columns
3. **SQL Builder** — select a table, pick columns, enter a WHERE clause, click SELECT / INSERT / UPDATE / DELETE
4. **Saved Queries** — save any generated SQL for later, copy with one click

---

## Sending Feedback

Click **Send Feedback** inside the app or visit:  
[https://github.com/kiranbeethoju/sqlAssist/issues/new](https://github.com/kiranbeethoju/sqlAssist/issues/new)

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `pyinstaller` not found | `python -m PyInstaller` or add Python's Scripts folder to PATH |
| App doesn't start on another PC | Build on the target OS |
| Antivirus flags the EXE | False positive — add an exception, or sign with `sign_exe.ps1` |
| SmartScreen still warns after signing | Get an EV cert from DigiCert / Sectigo for immediate trust |
| Icon not showing on macOS dock | Run the built `.app` from `dist/` rather than the raw `.py` script |

---

## License

Provided as-is for personal and commercial use.
