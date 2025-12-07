import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import csv
import io
import webbrowser
from collections import Counter


class CSVOperationsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Operations - By Kiran Beethoju")
        self.root.geometry("850x800")
        self.root.resizable(True, True)
        
        # Configure colors
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
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configure colorful styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Action.TButton', 
                       background='#4CAF50', 
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        style.map('Action.TButton',
                 background=[('active', '#45a049'), ('pressed', '#3d8b40')])
        
        style.configure('Control.TButton',
                       background='#2196F3',
                       foreground='white',
                       font=('Arial', 9),
                       padding=8)
        style.map('Control.TButton',
                 background=[('active', '#0b7dda'), ('pressed', '#0a6bc2')])
        
        style.configure('Reset.TButton',
                       background='#ff9800',
                       foreground='white',
                       font=('Arial', 9),
                       padding=8)
        style.map('Reset.TButton',
                 background=[('active', '#e68900'), ('pressed', '#cc7700')])
        
        style.configure('Help.TButton',
                       background='#9c27b0',
                       foreground='white',
                       font=('Arial', 9),
                       padding=8)
        style.map('Help.TButton',
                 background=[('active', '#7b1fa2'), ('pressed', '#6a1b9a')])
        
        # Configure label frame styles
        style.configure('Header.TLabelframe', 
                      background='#f0f0f0',
                      borderwidth=0)
        style.configure('Header.TLabelframe.Label',
                       background='#f0f0f0',
                       foreground='#1976D2',
                       font=('Arial', 11, 'bold'))
        
    def setup_ui(self):
        # Main container with background color
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Header Section with Author
        header_frame = tk.Frame(main_frame, bg="#e3f2fd", relief=tk.RAISED, bd=2, padx=15, pady=10)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with color
        title_label = tk.Label(header_frame, text="CSV Operations", 
                               font=("Arial", 18, "bold"), 
                               bg="#e3f2fd", 
                               fg="#1565C0")
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Author with color
        author_label = tk.Label(header_frame, text="By Kiran Beethoju", 
                               font=("Arial", 11, "italic"), 
                               bg="#e3f2fd", 
                               fg="#424242")
        author_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # GitHub Repository Link
        repo_url = "https://github.com/kiranbeethoju/sqlAssist"
        repo_label = tk.Label(header_frame, text=repo_url, 
                             font=("Arial", 9), 
                             bg="#e3f2fd",
                             fg="#1976D2", 
                             cursor="hand2",
                             underline=True)
        repo_label.grid(row=2, column=0, sticky=tk.W, pady=(2, 0))
        repo_label.bind("<Button-1>", lambda e: self.open_url(repo_url))
        repo_label.bind("<Enter>", lambda e: repo_label.config(fg="#0d47a1"))
        repo_label.bind("<Leave>", lambda e: repo_label.config(fg="#1976D2"))
        
        # CSV Data Section
        csv_frame = ttk.LabelFrame(main_frame, text="CSV Data", padding="5")
        csv_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        csv_frame.columnconfigure(0, weight=1)
        csv_frame.rowconfigure(0, weight=1)
        
        self.csv_text = scrolledtext.ScrolledText(csv_frame, height=8, wrap=tk.NONE, 
                                                   font=("Consolas", 10),
                                                   bg="#ffffff", fg="#212121")
        self.csv_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="8")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Input delimiter
        input_label = tk.Label(options_frame, text="Input delimiter:", 
                              bg="#f0f0f0", fg="#424242", font=("Arial", 9, "bold"))
        input_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        input_delim_combo = ttk.Combobox(options_frame, textvariable=self.input_delimiter, 
                                         values=["LF", "CR", "CRLF", ", (Comma)", "; (Semicolon)", "| (Pipe)", "Tab"], 
                                         state="readonly", width=18)
        input_delim_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Output delimiter
        output_label = tk.Label(options_frame, text="Output delimiter:", 
                               bg="#f0f0f0", fg="#424242", font=("Arial", 9, "bold"))
        output_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        output_delim_combo = ttk.Combobox(options_frame, textvariable=self.output_delimiter,
                                          values=[", (Comma)", "; (Semicolon)", "| (Pipe)", "Tab", "LF", "CR", "CRLF"],
                                          state="readonly", width=18)
        output_delim_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Checkboxes
        checkbox_frame = tk.Frame(options_frame, bg="#f0f0f0")
        checkbox_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(12, 0))
        
        ttk.Checkbutton(checkbox_frame, text="Ignore enclosed quotes", 
                       variable=self.ignore_enclosed_quotes).grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Use single quotes", 
                       variable=self.use_single_quotes).grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Trim data", 
                       variable=self.trim_data).grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        ttk.Checkbutton(checkbox_frame, text="Use double quotes", 
                       variable=self.use_double_quotes).grid(row=0, column=3, sticky=tk.W)
        
        # Action Buttons
        action_frame = tk.Frame(options_frame, bg="#f0f0f0")
        action_frame.grid(row=2, column=0, columnspan=4, pady=(12, 0))
        
        prepare_btn = ttk.Button(action_frame, text="Prepare CSV", 
                                command=self.prepare_csv, 
                                style='Action.TButton')
        prepare_btn.grid(row=0, column=0, padx=5)
        
        unique_btn = ttk.Button(action_frame, text="Get Unique", 
                              command=self.get_unique, 
                              style='Action.TButton')
        unique_btn.grid(row=0, column=1, padx=5)
        
        duplicates_btn = ttk.Button(action_frame, text="Get Duplicates", 
                                  command=self.get_duplicates, 
                                  style='Action.TButton')
        duplicates_btn.grid(row=0, column=2, padx=5)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, wrap=tk.NONE,
                                                     font=("Consolas", 10),
                                                     bg="#fff9c4", fg="#212121")
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary and Control Section
        summary_frame = tk.Frame(main_frame, bg="#f0f0f0")
        summary_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        summary_frame.columnconfigure(1, weight=1)
        
        # Summary labels with colors
        self.total_count_label = tk.Label(summary_frame, text="Total Count: 0", 
                                          bg="#f0f0f0", fg="#1976D2", 
                                          font=("Arial", 10, "bold"))
        self.total_count_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.unique_count_label = tk.Label(summary_frame, text="Unique records count: 0", 
                                           bg="#f0f0f0", fg="#388E3C", 
                                           font=("Arial", 10, "bold"))
        self.unique_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.duplicate_count_label = tk.Label(summary_frame, text="Duplicate records count: 0", 
                                              bg="#f0f0f0", fg="#D32F2F", 
                                              font=("Arial", 10, "bold"))
        self.duplicate_count_label.grid(row=0, column=2, sticky=tk.W)
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.grid(row=5, column=0, sticky=tk.E, pady=(12, 0))
        
        select_btn = ttk.Button(control_frame, text="Select All & Copy", 
                               command=self.select_all, 
                               style='Control.TButton')
        select_btn.grid(row=0, column=0, padx=5)
        
        reset_btn = ttk.Button(control_frame, text="Reset", 
                              command=self.reset, 
                              style='Reset.TButton')
        reset_btn.grid(row=0, column=1, padx=5)
        
        help_btn = ttk.Button(control_frame, text="Help", 
                             command=self.show_help, 
                             style='Help.TButton')
        help_btn.grid(row=0, column=2, padx=5)
        
    def get_delimiter_char(self, delimiter_name):
        """Convert delimiter name to actual character"""
        delimiter_map = {
            "LF": "\n",
            "CR": "\r",
            "CRLF": "\r\n",
            ", (Comma)": ",",
            "; (Semicolon)": ";",
            "| (Pipe)": "|",
            "Tab": "\t"
        }
        return delimiter_map.get(delimiter_name, ",")
    
    def parse_csv_data(self):
        """Parse CSV data from input text area"""
        input_text = self.csv_text.get("1.0", tk.END).strip()
        if not input_text:
            return []
        
        input_delim = self.get_delimiter_char(self.input_delimiter.get())
        
        # Handle different input formats
        lines = input_text.splitlines()
        if not lines:
            return []
        
        # Check if first line looks like headers
        data = []
        for line in lines:
            if line.strip():
                # Split by input delimiter
                if input_delim == "\n":
                    # If input is LF, treat each line as a separate field
                    data.append([line.strip()])
                else:
                    # Split by the delimiter
                    parts = line.split(input_delim)
                    if self.trim_data.get():
                        parts = [p.strip() for p in parts]
                    data.append(parts)
        
        return data
    
    def prepare_csv(self):
        """Prepare and format CSV data"""
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            
            self.csv_data = data
            
            # Get output delimiter
            output_delim = self.get_delimiter_char(self.output_delimiter.get())
            
            # Determine quote character
            quote_char = '"'
            if self.use_single_quotes.get():
                quote_char = "'"
            elif not self.use_double_quotes.get():
                quote_char = ""
            
            # Format output - ensure proper comma separation
            output_lines = []
            for row in data:
                if quote_char:
                    formatted_row = output_delim.join([f'{quote_char}{str(field)}{quote_char}' for field in row])
                else:
                    formatted_row = output_delim.join([str(field) for field in row])
                output_lines.append(formatted_row)
            
            # Join rows with newline, but keep delimiter within rows
            if output_delim in ["\n", "\r", "\r\n"]:
                # If delimiter is a line break, join with it
                output_text = output_delim.join(output_lines)
            else:
                # Otherwise, join rows with newlines, keeping delimiter within rows
                output_text = "\n".join(output_lines)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_text)
            
            # Update counts
            self.update_counts(len(data), len(data), 0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error preparing CSV: {str(e)}")
    
    def get_unique(self):
        """Get unique records from CSV data"""
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            
            self.csv_data = data
            
            # Convert rows to tuples for hashing
            seen = set()
            unique_data = []
            duplicates = []
            
            for row in data:
                row_tuple = tuple(row)
                if row_tuple in seen:
                    duplicates.append(row)
                else:
                    seen.add(row_tuple)
                    unique_data.append(row)
            
            self.unique_records = unique_data
            self.duplicate_records = duplicates
            
            # Format output
            output_delim = self.get_delimiter_char(self.output_delimiter.get())
            quote_char = '"'
            if self.use_single_quotes.get():
                quote_char = "'"
            elif not self.use_double_quotes.get():
                quote_char = ""
            
            output_lines = []
            for row in unique_data:
                if quote_char:
                    formatted_row = output_delim.join([f'{quote_char}{str(field)}{quote_char}' for field in row])
                else:
                    formatted_row = output_delim.join([str(field) for field in row])
                output_lines.append(formatted_row)
            
            if output_delim in ["\n", "\r", "\r\n"]:
                output_text = output_delim.join(output_lines)
            else:
                output_text = "\n".join(output_lines)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_text)
            
            # Update counts
            self.update_counts(len(data), len(unique_data), len(duplicates))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error getting unique records: {str(e)}")
    
    def get_duplicates(self):
        """Get duplicate records from CSV data"""
        try:
            data = self.parse_csv_data()
            if not data:
                messagebox.showwarning("Warning", "No data found in CSV Data section.")
                return
            
            self.csv_data = data
            
            # Find duplicates
            row_counter = Counter([tuple(row) for row in data])
            duplicates = [list(row) for row, count in row_counter.items() if count > 1]
            
            # Get all occurrences of duplicates
            duplicate_records = []
            seen_duplicates = set()
            for row in data:
                row_tuple = tuple(row)
                if row_counter[row_tuple] > 1:
                    if row_tuple not in seen_duplicates:
                        seen_duplicates.add(row_tuple)
                        duplicate_records.append(row)
            
            self.duplicate_records = duplicate_records
            
            # Format output
            output_delim = self.get_delimiter_char(self.output_delimiter.get())
            quote_char = '"'
            if self.use_single_quotes.get():
                quote_char = "'"
            elif not self.use_double_quotes.get():
                quote_char = ""
            
            output_lines = []
            for row in duplicate_records:
                if quote_char:
                    formatted_row = output_delim.join([f'{quote_char}{str(field)}{quote_char}' for field in row])
                else:
                    formatted_row = output_delim.join([str(field) for field in row])
                output_lines.append(formatted_row)
            
            if output_delim in ["\n", "\r", "\r\n"]:
                output_text = output_delim.join(output_lines)
            else:
                output_text = "\n".join(output_lines)
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_text)
            
            # Update counts
            unique_count = len(data) - len(duplicate_records)
            self.update_counts(len(data), unique_count, len(duplicate_records))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error getting duplicates: {str(e)}")
    
    def update_counts(self, total, unique, duplicates):
        """Update count labels"""
        self.total_count_label.config(text=f"Total Count: {total}")
        self.unique_count_label.config(text=f"Unique records count: {unique}")
        self.duplicate_count_label.config(text=f"Duplicate records count: {duplicates}")
    
    def select_all(self):
        """Select all text in output and copy to clipboard"""
        try:
            # Get all text from output
            content = self.output_text.get("1.0", tk.END).strip()
            
            if not content:
                messagebox.showinfo("Info", "No content to copy.")
                return
            
            # Clear clipboard and copy
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            
            # Also select in the text widget for visual feedback
            self.output_text.tag_add(tk.SEL, "1.0", tk.END)
            self.output_text.mark_set(tk.INSERT, "1.0")
            self.output_text.see(tk.INSERT)
            
            # Show confirmation
            messagebox.showinfo("Copied!", f"Content copied to clipboard!\n\n{len(content)} characters copied.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")
    
    def reset(self):
        """Reset all fields"""
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
    
    def open_url(self, url):
        """Open URL in default web browser"""
        webbrowser.open(url)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """CSV Operations - Help

1. Input your CSV data in the 'CSV Data' section (one row per line or use delimiters)

2. Configure options:
   - Input delimiter: How your input data is separated
   - Output delimiter: How you want the output formatted
   - Checkboxes: Formatting options for quotes and trimming

3. Use the action buttons:
   - Prepare CSV: Formats your data according to output settings
   - Get Unique: Shows only unique records
   - Get Duplicates: Shows only duplicate records

4. View results in the 'Output' section

5. Use control buttons:
   - Select All & Copy: Copies all output text to clipboard automatically
   - Reset: Clears all data and resets options
   - Help: Shows this help dialog

The summary section shows total, unique, and duplicate record counts."""
        
        messagebox.showinfo("Help", help_text)


def main():
    root = tk.Tk()
    app = CSVOperationsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
