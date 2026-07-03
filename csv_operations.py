import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import csv
import io
import os
import sys
import webbrowser
from collections import Counter

APP_VERSION = "1.1.0"
GITHUB_REPO = "https://github.com/kiranbeethoju/sqlAssist"
GITHUB_ISSUES = "https://github.com/kiranbeethoju/sqlAssist/issues/new"


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundles."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class CSVOperationsApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"CSV Operations v{APP_VERSION} - By Kiran Beethoju")
        self.root.geometry("900x820")
        self.root.minsize(700, 600)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.input_delimiter = tk.StringVar(value="LF")
        self.output_delimiter = tk.StringVar(value=", (Comma)")
        self.ignore_enclosed_quotes = tk.BooleanVar(value=False)
        self.use_single_quotes = tk.BooleanVar(value=False)
        self.trim_data = tk.BooleanVar(value=False)
        self.use_double_quotes = tk.BooleanVar(value=False)

        self.csv_data = []
        self.unique_records = []
        self.duplicate_records = []
        self._status_after_id = None

        self.setup_styles()
        self._set_app_icon()

        # Show the window immediately so users see it fast while UI builds
        self.root.update_idletasks()
        self.setup_ui()

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------
    def _set_app_icon(self):
        """Set the application window / dock icon from kblogo.png."""
        try:
            logo_path = resource_path("kblogo.png")
            if os.path.exists(logo_path):
                self._logo_img = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(True, self._logo_img)
        except Exception:
            pass  # Icon is cosmetic; silently skip if unavailable

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Action.TButton',
                        background='#4CAF50', foreground='white',
                        font=('Arial', 10, 'bold'), padding=10)
        style.map('Action.TButton',
                  background=[('active', '#45a049'), ('pressed', '#3d8b40')])

        style.configure('Control.TButton',
                        background='#2196F3', foreground='white',
                        font=('Arial', 9), padding=8)
        style.map('Control.TButton',
                  background=[('active', '#0b7dda'), ('pressed', '#0a6bc2')])

        style.configure('Reset.TButton',
                        background='#ff9800', foreground='white',
                        font=('Arial', 9), padding=8)
        style.map('Reset.TButton',
                  background=[('active', '#e68900'), ('pressed', '#cc7700')])

        style.configure('Help.TButton',
                        background='#9c27b0', foreground='white',
                        font=('Arial', 9), padding=8)
        style.map('Help.TButton',
                  background=[('active', '#7b1fa2'), ('pressed', '#6a1b9a')])

        style.configure('Feedback.TButton',
                        background='#E91E63', foreground='white',
                        font=('Arial', 9), padding=8)
        style.map('Feedback.TButton',
                  background=[('active', '#c2185b'), ('pressed', '#ad1457')])

        style.configure('Header.TLabelframe', background='#f0f0f0', borderwidth=0)
        style.configure('Header.TLabelframe.Label',
                        background='#f0f0f0', foreground='#1976D2',
                        font=('Arial', 11, 'bold'))

    # ------------------------------------------------------------------
    # UI Layout
    # ------------------------------------------------------------------
    def setup_ui(self):
        # ── Fixed bottom bar (packed first so it anchors at the bottom) ──
        bottom_bar = tk.Frame(self.root, bg="#e8e8e8", relief=tk.GROOVE, bd=1)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Status bar (toast notifications) – very bottom strip
        self.status_bar = tk.Label(
            bottom_bar, text="", bg="#e8e8e8", fg="#388E3C",
            font=("Arial", 9, "bold"), anchor=tk.W, padx=10, pady=3)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Summary counts row
        counts_frame = tk.Frame(bottom_bar, bg="#e8e8e8", padx=10, pady=6)
        counts_frame.pack(side=tk.TOP, fill=tk.X)

        self.total_count_label = tk.Label(
            counts_frame, text="Total Count: 0",
            bg="#e8e8e8", fg="#1976D2", font=("Arial", 10, "bold"))
        self.total_count_label.pack(side=tk.LEFT, padx=(0, 20))

        self.unique_count_label = tk.Label(
            counts_frame, text="Unique records count: 0",
            bg="#e8e8e8", fg="#388E3C", font=("Arial", 10, "bold"))
        self.unique_count_label.pack(side=tk.LEFT, padx=(0, 20))

        self.duplicate_count_label = tk.Label(
            counts_frame, text="Duplicate records count: 0",
            bg="#e8e8e8", fg="#D32F2F", font=("Arial", 10, "bold"))
        self.duplicate_count_label.pack(side=tk.LEFT)

        # Control buttons on the right side of the same row
        control_frame = tk.Frame(counts_frame, bg="#e8e8e8")
        control_frame.pack(side=tk.RIGHT)

        ttk.Button(control_frame, text="Select All & Copy",
                   command=self.select_all,
                   style='Control.TButton').pack(side=tk.LEFT, padx=4)

        ttk.Button(control_frame, text="Reset",
                   command=self.reset,
                   style='Reset.TButton').pack(side=tk.LEFT, padx=4)

        ttk.Button(control_frame, text="Send Feedback",
                   command=self.send_feedback,
                   style='Feedback.TButton').pack(side=tk.LEFT, padx=4)

        ttk.Button(control_frame, text="Help",
                   command=self.show_help,
                   style='Help.TButton').pack(side=tk.LEFT, padx=4)

        # ── Scrollable main content area ──
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=8)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=1)
        # Rows 1 (CSV Data) and 3 (Output) expand; others are fixed
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=2)

        # ── Header ──
        header_frame = tk.Frame(main_frame, bg="#e3f2fd",
                                relief=tk.RAISED, bd=2, padx=15, pady=8)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Logo thumbnail in header
        try:
            logo_path = resource_path("kblogo.png")
            if os.path.exists(logo_path):
                raw = tk.PhotoImage(file=logo_path)
                # Subsample to fit a small header thumbnail (~40x40)
                factor = max(1, raw.width() // 40)
                self._header_logo = raw.subsample(factor, factor)
                tk.Label(header_frame, image=self._header_logo,
                         bg="#e3f2fd").grid(row=0, column=0, rowspan=3,
                                            sticky=tk.W, padx=(0, 12))
        except Exception:
            pass

        title_col = 1
        tk.Label(header_frame,
                 text="CSV Operations",
                 font=("Arial", 18, "bold"),
                 bg="#e3f2fd", fg="#1565C0").grid(
            row=0, column=title_col, sticky=tk.W)

        tk.Label(header_frame,
                 text=f"By Kiran Beethoju  •  v{APP_VERSION}",
                 font=("Arial", 10, "italic"),
                 bg="#e3f2fd", fg="#424242").grid(
            row=1, column=title_col, sticky=tk.W, pady=(2, 0))

        repo_label = tk.Label(header_frame,
                              text=GITHUB_REPO,
                              font=("Arial", 9),
                              bg="#e3f2fd", fg="#1976D2",
                              cursor="hand2", underline=True)
        repo_label.grid(row=2, column=title_col, sticky=tk.W, pady=(2, 0))
        repo_label.bind("<Button-1>", lambda e: self.open_url(GITHUB_REPO))
        repo_label.bind("<Enter>", lambda e: repo_label.config(fg="#0d47a1"))
        repo_label.bind("<Leave>", lambda e: repo_label.config(fg="#1976D2"))

        # ── CSV Data input ──
        csv_frame = ttk.LabelFrame(main_frame, text="CSV Data", padding="5")
        csv_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))
        csv_frame.columnconfigure(0, weight=1)
        csv_frame.rowconfigure(0, weight=1)

        self.csv_text = scrolledtext.ScrolledText(
            csv_frame, height=7, wrap=tk.NONE,
            font=("Consolas", 10), bg="#ffffff", fg="#212121")
        self.csv_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ── Options ──
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="8")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_frame.columnconfigure(1, weight=1)

        tk.Label(options_frame, text="Input delimiter:",
                 bg="#f0f0f0", fg="#424242",
                 font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Combobox(options_frame, textvariable=self.input_delimiter,
                     values=["LF", "CR", "CRLF", ", (Comma)",
                             "; (Semicolon)", "| (Pipe)", "Tab"],
                     state="readonly", width=18).grid(
            row=0, column=1, sticky=tk.W, padx=(0, 20))

        tk.Label(options_frame, text="Output delimiter:",
                 bg="#f0f0f0", fg="#424242",
                 font=("Arial", 9, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
        ttk.Combobox(options_frame, textvariable=self.output_delimiter,
                     values=[", (Comma)", "; (Semicolon)", "| (Pipe)",
                             "Tab", "LF", "CR", "CRLF"],
                     state="readonly", width=18).grid(
            row=0, column=3, sticky=tk.W)

        checkbox_frame = tk.Frame(options_frame, bg="#f0f0f0")
        checkbox_frame.grid(row=1, column=0, columnspan=4,
                            sticky=tk.W, pady=(10, 0))

        ttk.Checkbutton(checkbox_frame, text="Ignore enclosed quotes",
                        variable=self.ignore_enclosed_quotes).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Use single quotes",
                        variable=self.use_single_quotes).grid(
            row=0, column=1, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Trim data",
                        variable=self.trim_data).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Use double quotes",
                        variable=self.use_double_quotes).grid(
            row=0, column=3, sticky=tk.W)

        action_frame = tk.Frame(options_frame, bg="#f0f0f0")
        action_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(action_frame, text="Prepare CSV",
                   command=self.prepare_csv,
                   style='Action.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Get Unique",
                   command=self.get_unique,
                   style='Action.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Get Duplicates",
                   command=self.get_duplicates,
                   style='Action.TButton').grid(row=0, column=2, padx=5)

        # ── Output ──
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=3, column=0,
                          sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 6))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=9, wrap=tk.NONE,
            font=("Consolas", 10), bg="#fff9c4", fg="#212121")
        self.output_text.grid(row=0, column=0,
                              sticky=(tk.W, tk.E, tk.N, tk.S))

    # ------------------------------------------------------------------
    # Status bar (non-blocking toast)
    # ------------------------------------------------------------------
    def show_status(self, message, color="#388E3C", duration_ms=3000):
        """Show a temporary status message in the bottom bar."""
        if self._status_after_id:
            self.root.after_cancel(self._status_after_id)
        self.status_bar.config(text=message, fg=color)
        self._status_after_id = self.root.after(
            duration_ms, lambda: self.status_bar.config(text=""))

    # ------------------------------------------------------------------
    # Delimiter helper
    # ------------------------------------------------------------------
    def get_delimiter_char(self, delimiter_name):
        delimiter_map = {
            "LF": "\n", "CR": "\r", "CRLF": "\r\n",
            ", (Comma)": ",", "; (Semicolon)": ";",
            "| (Pipe)": "|", "Tab": "\t"
        }
        return delimiter_map.get(delimiter_name, ",")

    # ------------------------------------------------------------------
    # CSV parsing
    # ------------------------------------------------------------------
    def parse_csv_data(self):
        input_text = self.csv_text.get("1.0", tk.END).strip()
        if not input_text:
            return []

        input_delim = self.get_delimiter_char(self.input_delimiter.get())
        lines = input_text.splitlines()
        data = []
        for line in lines:
            if line.strip():
                if input_delim == "\n":
                    data.append([line.strip()])
                else:
                    parts = line.split(input_delim)
                    if self.trim_data.get():
                        parts = [p.strip() for p in parts]
                    data.append(parts)
        return data

    # ------------------------------------------------------------------
    # Output formatting helper
    # ------------------------------------------------------------------
    def _format_output(self, rows):
        output_delim = self.get_delimiter_char(self.output_delimiter.get())
        quote_char = '"'
        if self.use_single_quotes.get():
            quote_char = "'"
        elif not self.use_double_quotes.get():
            quote_char = ""

        if output_delim in ("\n", "\r", "\r\n"):
            lines = []
            for row in rows:
                if quote_char:
                    lines.append(output_delim.join(
                        f'{quote_char}{field}{quote_char}' for field in row))
                else:
                    lines.append(output_delim.join(str(f) for f in row))
            return output_delim.join(lines)
        else:
            all_values = []
            for row in rows:
                for field in row:
                    if quote_char:
                        all_values.append(f'{quote_char}{field}{quote_char}')
                    else:
                        all_values.append(str(field))
            return output_delim.join(all_values)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def prepare_csv(self):
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            self.csv_data = data
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._format_output(data))
            self.update_counts(len(data), len(data), 0)
            self.show_status(f"✓ CSV prepared — {len(data)} records")
        except Exception as e:
            messagebox.showerror("Error", f"Error preparing CSV: {e}")

    def get_unique(self):
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            self.csv_data = data
            seen = set()
            unique_data, duplicates = [], []
            for row in data:
                t = tuple(row)
                if t in seen:
                    duplicates.append(row)
                else:
                    seen.add(t)
                    unique_data.append(row)
            self.unique_records = unique_data
            self.duplicate_records = duplicates
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._format_output(unique_data))
            self.update_counts(len(data), len(unique_data), len(duplicates))
            self.show_status(
                f"✓ Unique extracted — {len(unique_data)} unique, "
                f"{len(duplicates)} duplicates removed")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting unique records: {e}")

    def get_duplicates(self):
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            self.csv_data = data
            row_counter = Counter(tuple(row) for row in data)
            seen_dup = set()
            duplicate_records = []
            for row in data:
                t = tuple(row)
                if row_counter[t] > 1 and t not in seen_dup:
                    seen_dup.add(t)
                    duplicate_records.append(row)
            self.duplicate_records = duplicate_records
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._format_output(duplicate_records))
            unique_count = len(data) - len(duplicate_records)
            self.update_counts(len(data), unique_count, len(duplicate_records))
            self.show_status(
                f"✓ Found {len(duplicate_records)} duplicate record(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting duplicates: {e}")

    def update_counts(self, total, unique, duplicates):
        self.total_count_label.config(text=f"Total Count: {total}")
        self.unique_count_label.config(text=f"Unique records count: {unique}")
        self.duplicate_count_label.config(
            text=f"Duplicate records count: {duplicates}")

    def select_all(self):
        try:
            content = self.output_text.get("1.0", tk.END).strip()
            if not content:
                self.show_status("⚠  No content to copy", color="#E65100")
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.output_text.tag_add(tk.SEL, "1.0", tk.END)
            self.output_text.mark_set(tk.INSERT, "1.0")
            self.output_text.see(tk.INSERT)
            self.show_status(
                f"✓ Copied to clipboard — {len(content):,} characters")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying to clipboard: {e}")

    def reset(self):
        self.csv_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.input_delimiter.set("LF")
        self.output_delimiter.set(", (Comma)")
        self.ignore_enclosed_quotes.set(False)
        self.use_single_quotes.set(False)
        self.trim_data.set(False)
        self.use_double_quotes.set(False)
        self.update_counts(0, 0, 0)
        self.csv_data = []
        self.unique_records = []
        self.duplicate_records = []
        self.show_status("✓ Reset complete", color="#1976D2")

    def open_url(self, url):
        webbrowser.open(url)

    def send_feedback(self):
        """Open GitHub Issues page so users can post feedback directly."""
        self.open_url(GITHUB_ISSUES)
        self.show_status("✓ Opening GitHub Issues in your browser…", color="#E91E63")

    def show_help(self):
        help_text = f"""CSV Operations v{APP_VERSION} — Help

1. Paste your CSV data in the 'CSV Data' section (one row per line or delimited)

2. Configure Options:
   • Input delimiter  — how your input data is separated
   • Output delimiter — how you want the output formatted
   • Checkboxes       — quote styles and whitespace trimming

3. Action Buttons:
   • Prepare CSV   — format data with current settings
   • Get Unique    — show only unique records
   • Get Duplicates — show only duplicate records

4. Bottom Bar:
   • Summary counts update automatically after each action
   • Select All & Copy — copies output to clipboard (no popup)
   • Reset         — clears all data and settings
   • Send Feedback — open GitHub Issues to report bugs or ideas
   • Help          — show this dialog

GitHub: {GITHUB_REPO}"""
        messagebox.showinfo("Help", help_text)


def main():
    root = tk.Tk()
    # Withdraw until fully built to avoid white-flash on slower systems
    root.withdraw()
    app = CSVOperationsApp(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
