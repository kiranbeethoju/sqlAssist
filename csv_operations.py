import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import os
import sys
import json
import uuid
import datetime
import webbrowser
from pathlib import Path
from collections import Counter

APP_VERSION  = "1.2.0"
GITHUB_REPO  = "https://github.com/kiranbeethoju/sqlAssist"
GITHUB_ISSUES = "https://github.com/kiranbeethoju/sqlAssist/issues/new"

CONFIG_DIR  = Path.home() / ".csvoperations"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "databases": {},
    "saved_queries": [],
    "preferences": {
        "font_size": 10,
        "use_single_quotes": True,
        "trim_data": True,
        "input_delimiter": "LF",
        "output_delimiter": ", (Comma)"
    }
}


def resource_path(relative_path):
    """Resolve path for both dev mode and PyInstaller bundles."""
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


# ─────────────────────────────────────────────────────────────────────────────

class CSVOperationsApp:

    def __init__(self, root):
        self.root = root
        self.root.title(f"CSV Operations v{APP_VERSION} — By Kiran Beethoju")
        self.root.geometry("1000x900")
        self.root.minsize(820, 660)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Load persisted config
        self.config = self._load_config()
        prefs = self.config.get("preferences", {})

        # ── tkinter variables ──────────────────────────────────────────────
        self.font_size = tk.IntVar(value=prefs.get("font_size", 10))

        # CSV tab
        self.input_delimiter  = tk.StringVar(value=prefs.get("input_delimiter",  "LF"))
        self.output_delimiter = tk.StringVar(value=prefs.get("output_delimiter", ", (Comma)"))
        self.ignore_enclosed_quotes = tk.BooleanVar(value=False)
        self.use_single_quotes      = tk.BooleanVar(value=prefs.get("use_single_quotes", True))
        self.trim_data              = tk.BooleanVar(value=prefs.get("trim_data",          True))
        self.use_double_quotes      = tk.BooleanVar(value=False)

        # SQL Builder
        self.selected_db    = tk.StringVar()
        self.selected_table = tk.StringVar()
        self.column_vars    = {}          # col_name → BooleanVar
        self.where_clause   = tk.StringVar()

        # CSV data state
        self.csv_data          = []
        self.unique_records    = []
        self.duplicate_records = []

        # DB Config state
        self._cfg_db    = None
        self._cfg_table = None

        # Status timer
        self._status_job = None

        self.setup_styles()
        self._set_app_icon()
        self.root.update_idletasks()
        self.setup_ui()
        self._bind_zoom()

    # ── Config ────────────────────────────────────────────────────────────

    def _load_config(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                merged = {**DEFAULT_CONFIG, **data}
                merged["preferences"] = {
                    **DEFAULT_CONFIG["preferences"],
                    **data.get("preferences", {})
                }
                return merged
        except Exception:
            pass
        return {**DEFAULT_CONFIG}

    def _save_config(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            self.config["preferences"].update({
                "font_size":        self.font_size.get(),
                "use_single_quotes": self.use_single_quotes.get(),
                "trim_data":        self.trim_data.get(),
                "input_delimiter":  self.input_delimiter.get(),
                "output_delimiter": self.output_delimiter.get(),
            })
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ── App icon ──────────────────────────────────────────────────────────

    def _set_app_icon(self):
        try:
            path = resource_path("kblogo.png")
            if os.path.exists(path):
                self._logo_img = tk.PhotoImage(file=path)
                self.root.iconphoto(True, self._logo_img)
        except Exception:
            pass

    # ── Styles ────────────────────────────────────────────────────────────

    def setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        BTN_DEFS = [
            ("Action.TButton",     "#4CAF50", "#45a049"),
            ("Control.TButton",    "#2196F3", "#0b7dda"),
            ("Reset.TButton",      "#ff9800", "#e68900"),
            ("Help.TButton",       "#9c27b0", "#7b1fa2"),
            ("Feedback.TButton",   "#E91E63", "#c2185b"),
            ("SQL.TButton",        "#00796B", "#004D40"),
            ("Save.TButton",       "#5C6BC0", "#3949AB"),
            ("Delete.TButton",     "#c62828", "#b71c1c"),
            ("Capitalize.TButton", "#FF6F00", "#E65100"),
        ]
        for name, bg, active in BTN_DEFS:
            s.configure(name, background=bg, foreground="white",
                        font=("Arial", 9, "bold"), padding=7)
            s.map(name, background=[("active", active), ("pressed", active)])

        s.configure("Action.TButton", font=("Arial", 10, "bold"), padding=10)
        s.configure("TNotebook.Tab",  font=("Arial", 10, "bold"), padding=(12, 6))
        s.configure("Header.TLabelframe.Label",
                    background="#f0f0f0", foreground="#1976D2",
                    font=("Arial", 11, "bold"))

    # ── Root UI scaffold ──────────────────────────────────────────────────

    def setup_ui(self):
        self._build_bottom_bar()   # pack(BOTTOM) first so it never gets hidden
        self._build_header()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        tabs = [
            ("  CSV Operations  ", self._build_csv_tab),
            ("  SQL Builder  ",    self._build_sql_tab),
            ("  Saved Queries  ",  self._build_saved_tab),
            ("  DB Config  ",      self._build_config_tab),
        ]
        for label, builder in tabs:
            frame = ttk.Frame(self.notebook, padding=6)
            self.notebook.add(frame, text=label)
            builder(frame)

    # ── Header ────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#e3f2fd", relief=tk.RAISED, bd=2,
                       padx=15, pady=8)
        hdr.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 0))

        # Logo
        try:
            path = resource_path("kblogo.png")
            if os.path.exists(path):
                raw = tk.PhotoImage(file=path)
                f = max(1, raw.width() // 42)
                self._hdr_logo = raw.subsample(f, f)
                tk.Label(hdr, image=self._hdr_logo,
                         bg="#e3f2fd").pack(side=tk.LEFT, padx=(0, 12))
        except Exception:
            pass

        # Offline badge (right side)
        tk.Label(hdr, text="◉  Offline App\nNo internet required",
                 font=("Arial", 8), bg="#e3f2fd", fg="#757575",
                 justify=tk.RIGHT).pack(side=tk.RIGHT, padx=(0, 4))

        # Title block
        info = tk.Frame(hdr, bg="#e3f2fd")
        info.pack(side=tk.LEFT)

        tk.Label(info, text="CSV Operations",
                 font=("Arial", 18, "bold"), bg="#e3f2fd",
                 fg="#1565C0").pack(anchor=tk.W)
        tk.Label(info, text=f"By Kiran Beethoju  •  v{APP_VERSION}",
                 font=("Arial", 10, "italic"), bg="#e3f2fd",
                 fg="#424242").pack(anchor=tk.W)
        lnk = tk.Label(info, text=GITHUB_REPO, font=("Arial", 9),
                        bg="#e3f2fd", fg="#1976D2",
                        cursor="hand2", underline=True)
        lnk.pack(anchor=tk.W)
        lnk.bind("<Button-1>", lambda e: self.open_url(GITHUB_REPO))
        lnk.bind("<Enter>", lambda e: lnk.config(fg="#0d47a1"))
        lnk.bind("<Leave>", lambda e: lnk.config(fg="#1976D2"))

    # ── Bottom bar ────────────────────────────────────────────────────────

    def _build_bottom_bar(self):
        btm = tk.Frame(self.root, bg="#dce0e8", relief=tk.GROOVE, bd=1)
        btm.pack(side=tk.BOTTOM, fill=tk.X)

        # Status toast strip
        self.status_bar = tk.Label(btm, text="", bg="#dce0e8",
                                   fg="#388E3C", font=("Arial", 9, "bold"),
                                   anchor=tk.W, padx=10, pady=3)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        row = tk.Frame(btm, bg="#dce0e8", padx=10, pady=6)
        row.pack(side=tk.TOP, fill=tk.X)

        # Summary counts (left)
        for attr, text, fg in [
            ("total_count_label",     "Total: 0",       "#1976D2"),
            ("unique_count_label",    "Unique: 0",      "#388E3C"),
            ("duplicate_count_label", "Duplicates: 0",  "#D32F2F"),
        ]:
            lbl = tk.Label(row, text=text, bg="#dce0e8", fg=fg,
                           font=("Arial", 10, "bold"))
            lbl.pack(side=tk.LEFT, padx=(0, 18))
            setattr(self, attr, lbl)

        # Font zoom (middle)
        zf = tk.Frame(row, bg="#dce0e8")
        zf.pack(side=tk.LEFT, padx=(20, 0))
        tk.Label(zf, text="Font:", bg="#dce0e8",
                 font=("Arial", 9)).pack(side=tk.LEFT)
        tk.Button(zf, text="−", command=self.zoom_out,
                  relief=tk.FLAT, bg="#b0bec5",
                  font=("Arial", 11, "bold"), width=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=2)
        self._font_lbl = tk.Label(zf, text=str(self.font_size.get()),
                                   bg="#dce0e8",
                                   font=("Arial", 9, "bold"), width=3)
        self._font_lbl.pack(side=tk.LEFT)
        tk.Button(zf, text="+", command=self.zoom_in,
                  relief=tk.FLAT, bg="#b0bec5",
                  font=("Arial", 11, "bold"), width=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=2)

        # Control buttons (right)
        ctrl = tk.Frame(row, bg="#dce0e8")
        ctrl.pack(side=tk.RIGHT)
        for text, cmd, style in [
            ("Select All & Copy", self.select_all,   "Control.TButton"),
            ("Reset",             self.reset,         "Reset.TButton"),
            ("Send Feedback",     self.send_feedback, "Feedback.TButton"),
            ("Help",              self.show_help,     "Help.TButton"),
        ]:
            ttk.Button(ctrl, text=text, command=cmd,
                       style=style).pack(side=tk.LEFT, padx=4)

    # ═══════════════════════════════════════════════════════════════════════
    # Tab 1 — CSV Operations
    # ═══════════════════════════════════════════════════════════════════════

    def _build_csv_tab(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)
        p.rowconfigure(2, weight=2)

        # Input
        inf = ttk.LabelFrame(p, text="CSV Data", padding=5)
        inf.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        inf.columnconfigure(0, weight=1)
        inf.rowconfigure(0, weight=1)
        self.csv_text = scrolledtext.ScrolledText(
            inf, height=7, wrap=tk.NONE,
            font=("Consolas", self.font_size.get()),
            bg="#ffffff", fg="#212121")
        self.csv_text.grid(row=0, column=0, sticky="nsew")

        # Options
        opt = ttk.LabelFrame(p, text="Options", padding=8)
        opt.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        opt.columnconfigure(1, weight=1)

        tk.Label(opt, text="Input delimiter:",
                 font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Combobox(opt, textvariable=self.input_delimiter,
                     values=["LF", "CR", "CRLF", ", (Comma)",
                             "; (Semicolon)", "| (Pipe)", "Tab"],
                     state="readonly", width=18).grid(
            row=0, column=1, sticky=tk.W, padx=(0, 20))
        tk.Label(opt, text="Output delimiter:",
                 font=("Arial", 9, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
        ttk.Combobox(opt, textvariable=self.output_delimiter,
                     values=[", (Comma)", "; (Semicolon)", "| (Pipe)",
                             "Tab", "LF", "CR", "CRLF"],
                     state="readonly", width=18).grid(
            row=0, column=3, sticky=tk.W)

        cbf = tk.Frame(opt)
        cbf.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        for i, (txt, var) in enumerate([
            ("Ignore enclosed quotes", self.ignore_enclosed_quotes),
            ("Use single quotes",      self.use_single_quotes),
            ("Trim data",              self.trim_data),
            ("Use double quotes",      self.use_double_quotes),
        ]):
            ttk.Checkbutton(cbf, text=txt, variable=var).grid(
                row=0, column=i, sticky=tk.W, padx=(0, 15))

        # Action buttons
        abf = tk.Frame(opt)
        abf.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        for i, (txt, cmd, sty) in enumerate([
            ("Prepare CSV",    self.prepare_csv,   "Action.TButton"),
            ("Get Unique",     self.get_unique,     "Action.TButton"),
            ("Get Duplicates", self.get_duplicates, "Action.TButton"),
            ("Capitalize All", self.capitalize_all, "Capitalize.TButton"),
        ]):
            ttk.Button(abf, text=txt, command=cmd,
                       style=sty).grid(row=0, column=i, padx=5)

        # Output
        outf = ttk.LabelFrame(p, text="Output", padding=5)
        outf.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
        outf.columnconfigure(0, weight=1)
        outf.rowconfigure(0, weight=1)
        self.output_text = scrolledtext.ScrolledText(
            outf, height=9, wrap=tk.NONE,
            font=("Consolas", self.font_size.get()),
            bg="#fff9c4", fg="#212121")
        self.output_text.grid(row=0, column=0, sticky="nsew")

    # ═══════════════════════════════════════════════════════════════════════
    # Tab 2 — SQL Builder
    # ═══════════════════════════════════════════════════════════════════════

    def _build_sql_tab(self, p):
        p.columnconfigure(0, minsize=270, weight=0)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(0, weight=1)

        # ── Left column selector panel ────────────────────────────────────
        left = ttk.LabelFrame(p, text="Select Columns", padding=8, width=270)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        left.grid_propagate(False)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(5, weight=1)

        tk.Label(left, text="Database:",
                 font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.db_combo = ttk.Combobox(left, textvariable=self.selected_db,
                                     state="readonly", width=28)
        self.db_combo.grid(row=1, column=0, sticky="ew", pady=(2, 8))
        self.db_combo.bind("<<ComboboxSelected>>", self._on_db_change)

        tk.Label(left, text="Table:",
                 font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W)
        self.table_combo = ttk.Combobox(left, textvariable=self.selected_table,
                                        state="readonly", width=28)
        self.table_combo.grid(row=3, column=0, sticky="ew", pady=(2, 8))
        self.table_combo.bind("<<ComboboxSelected>>", self._on_table_change)

        tk.Label(left, text="Columns:",
                 font=("Arial", 9, "bold")).grid(row=4, column=0, sticky=tk.W)

        # Scrollable checkboxes
        cc = tk.Frame(left, bd=1, relief=tk.SUNKEN)
        cc.grid(row=5, column=0, sticky="nsew", pady=(4, 0))
        cc.columnconfigure(0, weight=1)
        cc.rowconfigure(0, weight=1)

        self._col_canvas = tk.Canvas(cc, bg="white")
        csb = ttk.Scrollbar(cc, orient="vertical", command=self._col_canvas.yview)
        self._col_canvas.configure(yscrollcommand=csb.set)
        csb.pack(side=tk.RIGHT, fill=tk.Y)
        self._col_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._col_inner = tk.Frame(self._col_canvas, bg="white")
        self._col_canvas.create_window((0, 0), window=self._col_inner,
                                       anchor="nw")
        self._col_inner.bind(
            "<Configure>",
            lambda e: self._col_canvas.configure(
                scrollregion=self._col_canvas.bbox("all")))

        # Select-all / none links
        selrow = tk.Frame(left)
        selrow.grid(row=6, column=0, pady=(6, 0))
        for txt, fn in [("All", self._cols_all), ("None", self._cols_none)]:
            tk.Button(selrow, text=f"Select {txt}", relief=tk.FLAT,
                      bg="#e3f2fd" if txt == "All" else "#fce4ec",
                      font=("Arial", 8), cursor="hand2",
                      command=fn).pack(side=tk.LEFT, padx=4)

        # ── Right query area ──────────────────────────────────────────────
        right = tk.Frame(p)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        # WHERE clause
        wf = tk.Frame(right)
        wf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        wf.columnconfigure(1, weight=1)
        tk.Label(wf, text="WHERE clause:",
                 font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6))
        ttk.Entry(wf, textvariable=self.where_clause,
                  font=("Consolas", 10)).grid(row=0, column=1, sticky="ew")

        # CRUD buttons
        crud = ttk.LabelFrame(right, text="Generate SQL Query", padding=8)
        crud.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        for i, qt in enumerate(["SELECT", "INSERT", "UPDATE", "DELETE"]):
            ttk.Button(crud, text=qt,
                       command=lambda t=qt: self.generate_sql(t),
                       style="SQL.TButton").grid(row=0, column=i, padx=6)

        # SQL output
        sqf = ttk.LabelFrame(right, text="Generated SQL", padding=5)
        sqf.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
        sqf.columnconfigure(0, weight=1)
        sqf.rowconfigure(0, weight=1)
        self.sql_output = scrolledtext.ScrolledText(
            sqf, height=10, wrap=tk.WORD,
            font=("Consolas", self.font_size.get()),
            bg="#e8f5e9", fg="#1b5e20")
        self.sql_output.grid(row=0, column=0, sticky="nsew")

        # SQL action row
        sbr = tk.Frame(right)
        sbr.grid(row=3, column=0, sticky="e", pady=(6, 0))
        ttk.Button(sbr, text="Copy SQL",
                   command=self.copy_sql,
                   style="Control.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(sbr, text="Save Query",
                   command=self.save_current_query,
                   style="Save.TButton").pack(side=tk.LEFT, padx=4)

        self._refresh_db_combo()

    # ═══════════════════════════════════════════════════════════════════════
    # Tab 3 — Saved Queries
    # ═══════════════════════════════════════════════════════════════════════

    def _build_saved_tab(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)

        tk.Label(p, text="Double-click a query to load it into SQL Builder",
                 font=("Arial", 9, "italic"), fg="#757575").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 6))

        tf = tk.Frame(p)
        tf.grid(row=1, column=0, sticky="nsew")
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(0, weight=1)

        cols = ("name", "query", "created")
        self.saved_tree = ttk.Treeview(tf, columns=cols,
                                       show="headings", selectmode="browse")
        self.saved_tree.heading("name",    text="Name")
        self.saved_tree.heading("query",   text="Query")
        self.saved_tree.heading("created", text="Created")
        self.saved_tree.column("name",    width=190, minwidth=130)
        self.saved_tree.column("query",   width=460, minwidth=200)
        self.saved_tree.column("created", width=100, minwidth=80)
        self.saved_tree.grid(row=0, column=0, sticky="nsew")
        self.saved_tree.bind("<Double-1>", self._load_saved_query)

        tsb = ttk.Scrollbar(tf, orient="vertical",
                            command=self.saved_tree.yview)
        tsb.grid(row=0, column=1, sticky="ns")
        self.saved_tree.configure(yscrollcommand=tsb.set)

        br = tk.Frame(p)
        br.grid(row=2, column=0, sticky="e", pady=(8, 0))
        for txt, cmd, sty in [
            ("Copy Selected",  self.copy_saved_query,   "Control.TButton"),
            ("Rename",         self.rename_saved_query,  "Save.TButton"),
            ("Delete Selected",self.delete_saved_query,  "Delete.TButton"),
        ]:
            ttk.Button(br, text=txt, command=cmd,
                       style=sty).pack(side=tk.LEFT, padx=4)

        self._refresh_saved_tree()

    # ═══════════════════════════════════════════════════════════════════════
    # Tab 4 — DB Config
    # ═══════════════════════════════════════════════════════════════════════

    def _build_config_tab(self, p):
        p.columnconfigure(0, minsize=250, weight=0)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(0, weight=1)

        # ── Left: tree ────────────────────────────────────────────────────
        lf = ttk.LabelFrame(p, text="Databases & Tables",
                            padding=6, width=250)
        lf.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        lf.grid_propagate(False)
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)

        self.db_tree = ttk.Treeview(lf, show="tree", selectmode="browse")
        self.db_tree.grid(row=0, column=0, sticky="nsew")
        tsb = ttk.Scrollbar(lf, orient="vertical", command=self.db_tree.yview)
        tsb.grid(row=0, column=1, sticky="ns")
        self.db_tree.configure(yscrollcommand=tsb.set)
        self.db_tree.bind("<<TreeviewSelect>>", self._on_cfg_tree_select)

        tb = tk.Frame(lf)
        tb.grid(row=1, column=0, columnspan=2, pady=(6, 0))
        for txt, fn, bg in [
            ("+ Database", self.add_database,      "#e3f2fd"),
            ("+ Table",    self.add_table,          "#e8f5e9"),
            ("Delete",     self.delete_db_or_table, "#ffebee"),
        ]:
            tk.Button(tb, text=txt, command=fn, relief=tk.FLAT,
                      bg=bg, font=("Arial", 8),
                      cursor="hand2").pack(side=tk.LEFT, padx=3)

        # ── Right: column editor ──────────────────────────────────────────
        rf = ttk.LabelFrame(p, text="Columns", padding=8)
        rf.grid(row=0, column=1, sticky="nsew")
        rf.columnconfigure(0, weight=1)
        rf.rowconfigure(1, weight=1)

        self._cfg_lbl = tk.Label(rf, text="Select a table on the left",
                                  font=("Arial", 10, "italic"), fg="#9E9E9E")
        self._cfg_lbl.grid(row=0, column=0, sticky=tk.W, pady=(0, 6))

        clf = tk.Frame(rf, bd=1, relief=tk.SUNKEN)
        clf.grid(row=1, column=0, sticky="nsew")
        clf.columnconfigure(0, weight=1)
        clf.rowconfigure(0, weight=1)
        self.col_listbox = tk.Listbox(clf, selectmode=tk.EXTENDED,
                                      font=("Consolas", 10))
        self.col_listbox.grid(row=0, column=0, sticky="nsew")
        clsb = ttk.Scrollbar(clf, orient="vertical",
                              command=self.col_listbox.yview)
        clsb.grid(row=0, column=1, sticky="ns")
        self.col_listbox.configure(yscrollcommand=clsb.set)

        # Single column add
        row2 = tk.Frame(rf)
        row2.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        row2.columnconfigure(0, weight=1)
        self._new_col = tk.StringVar()
        ttk.Entry(row2, textvariable=self._new_col,
                  font=("Consolas", 10)).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(row2, text="Add Column",
                   command=self.add_column,
                   style="SQL.TButton").grid(row=0, column=1)

        # Bulk add
        row3 = tk.Frame(rf)
        row3.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        tk.Label(row3, text="Bulk add (comma-separated):",
                 font=("Arial", 8, "italic"), fg="#616161").pack(
            side=tk.LEFT, padx=(0, 6))
        self._bulk_col = tk.StringVar()
        ttk.Entry(row3, textvariable=self._bulk_col,
                  font=("Consolas", 10), width=30).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(row3, text="Add All", command=self.bulk_add_columns,
                  relief=tk.FLAT, bg="#e8f5e9",
                  font=("Arial", 8), cursor="hand2").pack(side=tk.LEFT)

        # Delete
        row4 = tk.Frame(rf)
        row4.grid(row=4, column=0, sticky="e", pady=(6, 0))
        ttk.Button(row4, text="Delete Selected Column(s)",
                   command=self.delete_columns,
                   style="Delete.TButton").pack()

        self._refresh_db_tree()

    # ═══════════════════════════════════════════════════════════════════════
    # Font Zoom
    # ═══════════════════════════════════════════════════════════════════════

    def _bind_zoom(self):
        for attr in ("csv_text", "output_text", "sql_output"):
            if hasattr(self, attr):
                w = getattr(self, attr)
                w.bind("<Control-MouseWheel>", self._on_ctrl_scroll)
                w.bind("<Control-Button-4>",   self._on_ctrl_scroll)
                w.bind("<Control-Button-5>",   self._on_ctrl_scroll)
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())
        self.root.bind("<Control-plus>",  lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())

    def _on_ctrl_scroll(self, event):
        delta = getattr(event, "delta", 0)
        num   = getattr(event, "num",   0)
        if delta > 0 or num == 4:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        if self.font_size.get() < 28:
            self.font_size.set(self.font_size.get() + 1)
            self._apply_font()

    def zoom_out(self):
        if self.font_size.get() > 7:
            self.font_size.set(self.font_size.get() - 1)
            self._apply_font()

    def _apply_font(self):
        sz = self.font_size.get()
        self._font_lbl.config(text=str(sz))
        for attr in ("csv_text", "output_text", "sql_output"):
            if hasattr(self, attr):
                getattr(self, attr).configure(font=("Consolas", sz))
        self._save_config()
        self.show_status(f"Font size: {sz}")

    # ═══════════════════════════════════════════════════════════════════════
    # SQL Builder helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _refresh_db_combo(self):
        dbs = list(self.config.get("databases", {}).keys())
        self.db_combo["values"] = dbs
        if dbs and not self.selected_db.get():
            self.selected_db.set(dbs[0])
            self._on_db_change()

    def _on_db_change(self, _=None):
        db = self.selected_db.get()
        tables = list(self.config["databases"].get(db, {})
                      .get("tables", {}).keys())
        self.table_combo["values"] = tables
        self.selected_table.set(tables[0] if tables else "")
        if tables:
            self._on_table_change()
        else:
            self._clear_col_boxes()

    def _on_table_change(self, _=None):
        db, tbl = self.selected_db.get(), self.selected_table.get()
        cols = (self.config["databases"].get(db, {})
                .get("tables", {}).get(tbl, {})
                .get("columns", []))
        self._build_col_checks(cols)

    def _build_col_checks(self, columns):
        for w in self._col_inner.winfo_children():
            w.destroy()
        self.column_vars = {}
        for col in columns:
            var = tk.BooleanVar(value=True)
            self.column_vars[col] = var
            ttk.Checkbutton(self._col_inner, text=col,
                            variable=var).pack(anchor=tk.W, padx=4, pady=1)
        self._col_canvas.update_idletasks()
        self._col_canvas.configure(
            scrollregion=self._col_canvas.bbox("all"))

    def _clear_col_boxes(self):
        for w in self._col_inner.winfo_children():
            w.destroy()
        self.column_vars = {}

    def _cols_all(self):
        for v in self.column_vars.values():
            v.set(True)

    def _cols_none(self):
        for v in self.column_vars.values():
            v.set(False)

    # ─── SQL generation ───────────────────────────────────────────────────

    def generate_sql(self, qtype):
        db  = self.selected_db.get()
        tbl = self.selected_table.get()
        if not db or not tbl:
            messagebox.showwarning(
                "SQL Builder",
                "Select a Database and Table first.\n"
                "(Configure them in the 'DB Config' tab.)")
            return

        sel_cols = [c for c, v in self.column_vars.items() if v.get()]
        if not sel_cols and qtype != "DELETE":
            messagebox.showwarning("SQL Builder",
                                   "Select at least one column.")
            return

        q = "'" if self.use_single_quotes.get() else '"'
        where_raw = self.where_clause.get().strip()
        where_sql = f" WHERE {where_raw}" if where_raw else " WHERE <condition>"

        if qtype == "SELECT":
            col_str = ", ".join(sel_cols)
            w = f"\nWHERE {where_raw}" if where_raw else ""
            sql = f"SELECT {col_str}\nFROM {tbl}{w};"

        elif qtype == "INSERT":
            col_str = ", ".join(sel_cols)
            val_str = ", ".join(
                f"{q}value{i+1}{q}" for i in range(len(sel_cols)))
            sql = (f"INSERT INTO {tbl}\n"
                   f"    ({col_str})\nVALUES\n"
                   f"    ({val_str});")

        elif qtype == "UPDATE":
            pairs = ",\n    ".join(
                f"{c} = {q}value{i+1}{q}"
                for i, c in enumerate(sel_cols))
            sql = f"UPDATE {tbl}\nSET\n    {pairs}{where_sql};"

        elif qtype == "DELETE":
            sql = f"DELETE FROM {tbl}{where_sql};"
        else:
            return

        self.sql_output.delete("1.0", tk.END)
        self.sql_output.insert("1.0", sql)
        self.show_status(f"✓ {qtype} query generated for [{tbl}]")

    def copy_sql(self):
        sql = self.sql_output.get("1.0", tk.END).strip()
        if not sql:
            self.show_status("⚠  No SQL to copy", color="#E65100")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(sql)
        self.show_status(f"✓ SQL copied — {len(sql):,} characters")

    def save_current_query(self):
        sql = self.sql_output.get("1.0", tk.END).strip()
        if not sql:
            messagebox.showwarning("Save Query", "No SQL to save.")
            return
        name = simpledialog.askstring(
            "Save Query", "Name for this query:", parent=self.root)
        if not name:
            return
        entry = {
            "id":      str(uuid.uuid4()),
            "name":    name.strip(),
            "query":   sql,
            "created": datetime.date.today().isoformat(),
        }
        self.config.setdefault("saved_queries", []).append(entry)
        self._save_config()
        self._refresh_saved_tree()
        self.show_status(f"✓ Saved '{name}'")

    # ═══════════════════════════════════════════════════════════════════════
    # Saved Queries helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _refresh_saved_tree(self):
        self.saved_tree.delete(*self.saved_tree.get_children())
        for q in self.config.get("saved_queries", []):
            preview = q["query"].replace("\n", " ")[:90]
            self.saved_tree.insert("", tk.END, iid=q["id"],
                                   values=(q["name"], preview,
                                           q.get("created", "")))

    def _load_saved_query(self, _=None):
        sel = self.saved_tree.selection()
        if not sel:
            return
        for q in self.config.get("saved_queries", []):
            if q["id"] == sel[0]:
                self.sql_output.delete("1.0", tk.END)
                self.sql_output.insert("1.0", q["query"])
                self.notebook.select(1)
                self.show_status(f"✓ Loaded '{q['name']}' into SQL Builder")
                return

    def copy_saved_query(self):
        sel = self.saved_tree.selection()
        if not sel:
            self.show_status("⚠  Select a query first", color="#E65100")
            return
        for q in self.config.get("saved_queries", []):
            if q["id"] == sel[0]:
                self.root.clipboard_clear()
                self.root.clipboard_append(q["query"])
                self.show_status(f"✓ Copied '{q['name']}'")
                return

    def rename_saved_query(self):
        sel = self.saved_tree.selection()
        if not sel:
            self.show_status("⚠  Select a query to rename", color="#E65100")
            return
        for q in self.config.get("saved_queries", []):
            if q["id"] == sel[0]:
                new = simpledialog.askstring(
                    "Rename", "New name:", initialvalue=q["name"],
                    parent=self.root)
                if new:
                    q["name"] = new.strip()
                    self._save_config()
                    self._refresh_saved_tree()
                    self.show_status(f"✓ Renamed to '{new}'")
                return

    def delete_saved_query(self):
        sel = self.saved_tree.selection()
        if not sel:
            self.show_status("⚠  Select a query to delete", color="#E65100")
            return
        qid  = sel[0]
        qs   = self.config.get("saved_queries", [])
        name = next((q["name"] for q in qs if q["id"] == qid), "")
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            self.config["saved_queries"] = [q for q in qs if q["id"] != qid]
            self._save_config()
            self._refresh_saved_tree()
            self.show_status(f"✓ Deleted '{name}'")

    # ═══════════════════════════════════════════════════════════════════════
    # DB Config helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _refresh_db_tree(self):
        self.db_tree.delete(*self.db_tree.get_children())
        for db, ddata in self.config.get("databases", {}).items():
            node = self.db_tree.insert("", tk.END, iid=f"db::{db}",
                                       text=f"🗄  {db}", open=True)
            for tbl in ddata.get("tables", {}).keys():
                self.db_tree.insert(node, tk.END,
                                    iid=f"tbl::{db}::{tbl}",
                                    text=f"    📋  {tbl}")

    def _on_cfg_tree_select(self, _=None):
        sel = self.db_tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("tbl::"):
            _, db, tbl = iid.split("::", 2)
            self._cfg_db    = db
            self._cfg_table = tbl
            self._cfg_lbl.config(
                text=f"Columns  →  {db} · {tbl}",
                fg="#1565C0", font=("Arial", 10, "bold"))
            self._refresh_col_listbox()
        elif iid.startswith("db::"):
            self._cfg_db    = iid.split("::", 1)[1]
            self._cfg_table = None
            self._cfg_lbl.config(
                text=f"Select a table under {self._cfg_db}",
                fg="#9E9E9E", font=("Arial", 10, "italic"))
            self.col_listbox.delete(0, tk.END)

    def _refresh_col_listbox(self):
        self.col_listbox.delete(0, tk.END)
        if not self._cfg_db or not self._cfg_table:
            return
        cols = (self.config["databases"]
                .get(self._cfg_db, {})
                .get("tables", {})
                .get(self._cfg_table, {})
                .get("columns", []))
        for c in cols:
            self.col_listbox.insert(tk.END, c)

    def _db_tables(self, db):
        return (self.config.get("databases", {})
                .get(db, {}).get("tables", {}))

    def add_database(self):
        name = simpledialog.askstring("Add Database", "Database name:",
                                      parent=self.root)
        if not name:
            return
        name = name.strip()
        dbs  = self.config.setdefault("databases", {})
        if name in dbs:
            messagebox.showwarning("Add Database", f"'{name}' already exists.")
            return
        dbs[name] = {"tables": {}}
        self._save_config()
        self._refresh_db_tree()
        self._refresh_db_combo()
        self.show_status(f"✓ Database '{name}' added")

    def add_table(self):
        if not self._cfg_db:
            messagebox.showwarning("Add Table", "Select a database first.")
            return
        name = simpledialog.askstring("Add Table", "Table name:",
                                      parent=self.root)
        if not name:
            return
        name   = name.strip()
        tables = self.config["databases"][self._cfg_db].setdefault("tables", {})
        if name in tables:
            messagebox.showwarning("Add Table", f"Table '{name}' already exists.")
            return
        tables[name] = {"columns": []}
        self._save_config()
        self._refresh_db_tree()
        self._refresh_db_combo()
        self.show_status(f"✓ Table '{name}' added to '{self._cfg_db}'")

    def delete_db_or_table(self):
        sel = self.db_tree.selection()
        if not sel:
            self.show_status("⚠  Select a database or table to delete",
                             color="#E65100")
            return
        iid = sel[0]
        if iid.startswith("tbl::"):
            _, db, tbl = iid.split("::", 2)
            if messagebox.askyesno("Delete", f"Delete table '{tbl}'?"):
                self.config["databases"][db]["tables"].pop(tbl, None)
                self._cfg_table = None
                self.show_status(f"✓ Table '{tbl}' deleted")
        elif iid.startswith("db::"):
            db = iid.split("::", 1)[1]
            if messagebox.askyesno("Delete",
                                    f"Delete database '{db}' and all its tables?"):
                self.config["databases"].pop(db, None)
                self._cfg_db    = None
                self._cfg_table = None
                self.show_status(f"✓ Database '{db}' deleted")
        self._save_config()
        self._refresh_db_tree()
        self._refresh_db_combo()

    def add_column(self):
        col = self._new_col.get().strip()
        if not col:
            return
        if not self._cfg_db or not self._cfg_table:
            messagebox.showwarning("Add Column", "Select a table first.")
            return
        cols = (self.config["databases"][self._cfg_db]
                ["tables"][self._cfg_table].setdefault("columns", []))
        if col not in cols:
            cols.append(col)
            self._save_config()
            self._refresh_col_listbox()
            self._new_col.set("")
            self.show_status(f"✓ Column '{col}' added")

    def bulk_add_columns(self):
        raw = self._bulk_col.get().strip()
        if not raw:
            return
        if not self._cfg_db or not self._cfg_table:
            messagebox.showwarning("Bulk Add", "Select a table first.")
            return
        cols    = (self.config["databases"][self._cfg_db]
                   ["tables"][self._cfg_table].setdefault("columns", []))
        new     = [c.strip() for c in raw.split(",") if c.strip()]
        added   = [c for c in new if c not in cols]
        cols.extend(added)
        self._save_config()
        self._refresh_col_listbox()
        self._bulk_col.set("")
        self.show_status(f"✓ Added {len(added)} column(s)")

    def delete_columns(self):
        if not self._cfg_db or not self._cfg_table:
            return
        sels = self.col_listbox.curselection()
        if not sels:
            self.show_status("⚠  Select column(s) to delete", color="#E65100")
            return
        to_del = {self.col_listbox.get(i) for i in sels}
        target = (self.config["databases"][self._cfg_db]
                  ["tables"][self._cfg_table])
        target["columns"] = [c for c in target.get("columns", [])
                              if c not in to_del]
        self._save_config()
        self._refresh_col_listbox()
        self.show_status(f"✓ Deleted {len(to_del)} column(s)")

    # ═══════════════════════════════════════════════════════════════════════
    # Status toast
    # ═══════════════════════════════════════════════════════════════════════

    def show_status(self, msg, color="#388E3C", ms=3500):
        if self._status_job:
            self.root.after_cancel(self._status_job)
        self.status_bar.config(text=msg, fg=color)
        self._status_job = self.root.after(
            ms, lambda: self.status_bar.config(text=""))

    # ═══════════════════════════════════════════════════════════════════════
    # CSV Operations
    # ═══════════════════════════════════════════════════════════════════════

    def _delim(self, name):
        return {
            "LF": "\n", "CR": "\r", "CRLF": "\r\n",
            ", (Comma)": ",", "; (Semicolon)": ";",
            "| (Pipe)": "|", "Tab": "\t"
        }.get(name, ",")

    def _parse(self):
        text = self.csv_text.get("1.0", tk.END).strip()
        if not text:
            return []
        idl  = self._delim(self.input_delimiter.get())
        data = []
        for line in text.splitlines():
            if line.strip():
                if idl == "\n":
                    data.append([line.strip()])
                else:
                    parts = line.split(idl)
                    if self.trim_data.get():
                        parts = [p.strip() for p in parts]
                    data.append(parts)
        return data

    def _fmt(self, rows):
        odl = self._delim(self.output_delimiter.get())
        if self.use_single_quotes.get():
            qc = "'"
        elif self.use_double_quotes.get():
            qc = '"'
        else:
            qc = ""

        if odl in ("\n", "\r", "\r\n"):
            lines = []
            for row in rows:
                joined = odl.join(f"{qc}{f}{qc}" if qc else str(f)
                                  for f in row)
                lines.append(joined)
            return odl.join(lines)
        else:
            vals = []
            for row in rows:
                for f in row:
                    vals.append(f"{qc}{f}{qc}" if qc else str(f))
            return odl.join(vals)

    def prepare_csv(self):
        try:
            data = self._parse()
            if not data:
                messagebox.showwarning("Warning", "No data in CSV Data section.")
                return
            self.csv_data = data
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._fmt(data))
            self._set_counts(len(data), len(data), 0)
            self.show_status(f"✓ CSV prepared — {len(data)} records")
            self._save_config()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_unique(self):
        try:
            data = self._parse()
            if not data:
                messagebox.showwarning("Warning", "No data in CSV Data section.")
                return
            seen, uniq, dups = set(), [], []
            for row in data:
                t = tuple(row)
                (dups if t in seen else uniq).append(row)
                seen.add(t)
            self.csv_data, self.unique_records = data, uniq
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._fmt(uniq))
            self._set_counts(len(data), len(uniq), len(dups))
            self.show_status(
                f"✓ {len(uniq)} unique, {len(dups)} duplicates removed")
            self._save_config()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_duplicates(self):
        try:
            data = self._parse()
            if not data:
                messagebox.showwarning("Warning", "No data in CSV Data section.")
                return
            ctr = Counter(tuple(r) for r in data)
            seen, dups = set(), []
            for row in data:
                t = tuple(row)
                if ctr[t] > 1 and t not in seen:
                    seen.add(t)
                    dups.append(row)
            self.csv_data = data
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", self._fmt(dups))
            self._set_counts(len(data), len(data) - len(dups), len(dups))
            self.show_status(f"✓ Found {len(dups)} duplicate record(s)")
            self._save_config()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def capitalize_all(self):
        try:
            text = self.csv_text.get("1.0", tk.END).strip()
            if not text:
                self.show_status("⚠  No input to capitalize", color="#E65100")
                return
            upper = text.upper()
            self.csv_text.delete("1.0", tk.END)
            self.csv_text.insert("1.0", upper)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", upper)
            self.show_status("✓ Converted to UPPERCASE")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_counts(self, total, unique, dups):
        self.total_count_label.config(text=f"Total: {total}")
        self.unique_count_label.config(text=f"Unique: {unique}")
        self.duplicate_count_label.config(text=f"Duplicates: {dups}")

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
            self.show_status(f"✓ Copied — {len(content):,} characters")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset(self):
        self.csv_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.input_delimiter.set("LF")
        self.output_delimiter.set(", (Comma)")
        self.ignore_enclosed_quotes.set(False)
        self.use_single_quotes.set(True)
        self.trim_data.set(True)
        self.use_double_quotes.set(False)
        self._set_counts(0, 0, 0)
        self.csv_data = self.unique_records = self.duplicate_records = []
        self.show_status("✓ Reset complete", color="#1976D2")

    # ═══════════════════════════════════════════════════════════════════════
    # Misc
    # ═══════════════════════════════════════════════════════════════════════

    def open_url(self, url):
        webbrowser.open(url)

    def send_feedback(self):
        self.open_url(GITHUB_ISSUES)
        self.show_status("✓ Opening GitHub Issues…", color="#E91E63")

    def show_help(self):
        messagebox.showinfo("Help", f"""\
CSV Operations v{APP_VERSION} — Quick Guide

TABS
─────────────────────────────────────────────
CSV Operations  → paste data, format, dedupe,
                  capitalize, copy output

SQL Builder     → pick DB / table / columns,
                  generate SELECT / INSERT /
                  UPDATE / DELETE queries

Saved Queries   → browse, copy, rename, delete
                  your saved SQL queries

DB Config       → add databases, tables and
                  columns (persisted to disk)

CONTROLS
─────────────────────────────────────────────
Ctrl + scroll wheel  →  font zoom
Ctrl + = / −         →  font zoom
Select All & Copy    →  copies output (no popup)
Send Feedback        →  opens GitHub Issues

Config file: {CONFIG_FILE}
GitHub: {GITHUB_REPO}""")


# ─────────────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.withdraw()
    CSVOperationsApp(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
