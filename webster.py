import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, Text, Scrollbar
from tkintertable import TableCanvas, TableModel
import pandas as pd
import os
import webbrowser

global_df = None  # Global variable to store the DataFrame
current_cell = None

# Ensure directory creation
def ensure_dir(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Write HTML to file
def write_html(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
def parse_line_numbers(line_numbers):
    result = []
    parts = line_numbers.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start - 1, end))
        else:
            result.append(int(part) - 1)  # Convert to zero-based index
    return result
# Generate HTML Content
def generate_html_content(row):
    def check_nan(value):
        return "" if pd.isna(value) else value

    full_content = f"{check_nan(row['ourContent'])}{check_nan(row.get('Extra1', ''))}{check_nan(row.get('Extra2', ''))}"
    directory_mode = str(row.get('directoryMode', 'false')).strip().lower() == 'true'
    front_page = str(row.get('frontPage', 'false')).strip().lower() == 'true'
    canonical_url = row['websiteUrl'] if front_page and not directory_mode else f"{row['websiteUrl']}{row['ourUrl']}/" if directory_mode else f"{row['websiteUrl']}{row['ourUrl']}.{row.get('fileExtension', 'html')}"
    use_link_box = str(row.get('useLinkBox', 'false')).strip().lower() == 'true'

    link_box_html = ""
    if use_link_box:
        link_box_html = f"""<div style="width: 200px; margin: 0 auto;">
            <textarea id="linkCodeBox" readonly style="width: 100%; height: 60px; padding: 10px; border: 1px solid #ccc; resize: none;">&lt;a href="{canonical_url}"&gt;{check_nan(row['ourTitle'])}&lt;/a&gt;</textarea><br>
            <button onclick="copyLinkCode()" style="background-color: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer;">Copy HTML</button>
        </div>
        <script>
            function copyLinkCode() {{
                var linkCodeBox = document.getElementById('linkCodeBox');
                linkCodeBox.select();
                document.execCommand('copy');
                alert('HTML code copied to clipboard:\\n' + linkCodeBox.value);
            }}
        </script>"""

    return f"""<html><head>
        <title>{check_nan(row['ourTitle'])}</title>
        <meta name="description" content="{check_nan(row['ourMeta'])}">
        <link rel="canonical" href="{canonical_url}">
        <link rel="icon" href="{check_nan(row['Icon'])}" sizes="32x32">
        <link rel="stylesheet" href="{check_nan(row['styleSheet'])}">
        <meta property="og:title" content="{check_nan(row['ourTitle'])}">
        <meta property="og:url" content="{canonical_url}">
        <meta property="og:image" content="{check_nan(row['shareImageUrl'])}">
        <meta property="og:description" content="{check_nan(row['ourTitle'])}">
    </head><body>
        <div class="header">{check_nan(row['ourHeader'])}</div>
        <div class="topnav" id="myTopnav">{check_nan(row['topMenu'])}</div>
        <div class="content">
            <h2>{check_nan(row['ourTitle'])}</h2>
            {full_content}
            {link_box_html}
            {check_nan(row['ourShareButton'])}
        </div>
        <div class="footer">{check_nan(row['ourFooter'])}</div>
    </body></html>"""

def parse_line_numbers(line_numbers):
    result = []
    parts = line_numbers.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start - 1, end))
        else:
            result.append(int(part) - 1)  # Convert to zero-based index
    return result
# Construct the file path for a given row
def construct_file_path(row):
    folder_path = row['folderPath']
    directory_mode = str(row.get('directoryMode', 'false')).strip().lower() == 'true'
    file_name = os.path.join(row['ourUrl'], "index") if directory_mode else row['ourUrl']
    file_extension = row.get('fileExtension', 'html')
    return os.path.join(folder_path, f"{file_name}.{file_extension}")
# Publish Rows to Disk
def publish_rows_to_disk(line_numbers):
    global global_df

    if global_df is None:
        messagebox.showwarning("No CSV", "No CSV loaded. Please load a CSV file first.")
        return "No CSV loaded."

    try:
        lines_to_process = parse_line_numbers(line_numbers)
        output = []

        for index in lines_to_process:
            if index < len(global_df):
                row = global_df.iloc[index]
                folder_path = row['folderPath']

                directory_mode = str(row.get('directoryMode', 'false')).strip().lower() == 'true'
                file_name = os.path.join(row['ourUrl'], "index") if directory_mode else row['ourUrl']
                file_extension = row.get('fileExtension', 'html')
                full_path = os.path.join(folder_path, f"{file_name}.{file_extension}")

                ensure_dir(os.path.dirname(full_path))
                html_content = generate_html_content(row)
                write_html(html_content, full_path)
                output.append(f"Processed row {index + 1} and saved to {full_path}")

        return "\n".join(output)
    except Exception as e:
        return f"Error processing data: {str(e)}"

# View Html Pages
def view_html_pages(line_numbers=None):
    global global_df

    if global_df is None:
        messagebox.showwarning("No CSV", "No CSV loaded. Please load a CSV file first.")
        return "No CSV loaded."

    try:
        lines_to_open = parse_line_numbers(line_numbers)
        files_to_open = []

        for index in lines_to_open:
            if index < len(global_df):
                row = global_df.iloc[index]
                file_path = construct_file_path(row)
                files_to_open.append(file_path)

        if not files_to_open:
            messagebox.showwarning("No Files", "No valid files to open.")
            return "No valid files to open."

        for file in files_to_open:
            webbrowser.open(f"file://{os.path.abspath(file)}", new=2)
        return f"Opened {len(files_to_open)} files in the browser."
    except Exception as e:
        return f"Error opening files: {str(e)}"

# Load CSV
def load_csv():
    global global_df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        global_df = pd.read_csv(file_path)
        global_df = global_df.applymap(lambda x: "" if pd.isna(x) else x)  # Replace NaN with empty strings
        update_table()
        messagebox.showinfo("CSV Loaded", "CSV file loaded successfully.")
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load CSV: {str(e)}")

# Save CSV
def save_csv():
    global global_df
    if global_df is None:
        messagebox.showwarning("No CSV", "No CSV loaded. Please load a CSV file first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        global_df.to_csv(file_path, index=False)
        messagebox.showinfo("CSV Saved", f"CSV file saved successfully to {file_path}.")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save CSV: {str(e)}")

# Update Table
def update_table():
    global global_df
    if global_df is not None:
        data_dict = global_df.to_dict(orient="index")
        model = TableModel()
        model.importDict(data_dict)
        table.updateModel(model)
        table.redraw()

# Process Button Action
def process_button_action():
    row_numbers = simpledialog.askstring("Rows to Process", "Enter rows to process (e.g., 0-2,4,6-8):")
    if row_numbers:
        result = publish_rows_to_disk(row_numbers)
        messagebox.showinfo("Process Result", result)

# Open Button Action
def open_button_action():
    row_numbers = simpledialog.askstring("Rows to Open", "Enter rows to open (e.g., 0-2,4,6-8):")
    if row_numbers:
        result = view_html_pages(row_numbers)
        messagebox.showinfo("Open Result", result)

# Edit Cell
def edit_cell():
    global global_df, current_cell
    if global_df is None or current_cell is None:
        messagebox.showwarning("No Cell", "Please select a cell to edit.")
        return

    row, col = current_cell
    col_name = list(global_df.columns)[col]
    existing_content = global_df.iloc[row, col]

    def save_edit():
        new_content = text.get("1.0", tk.END).strip()
        global_df.at[row, col_name] = new_content
        edit_window.destroy()
        update_table()
        messagebox.showinfo("Edit Success", f"Successfully edited '{col_name}'")

    def cancel_edit(event=None):  # Optional event parameter for binding
        edit_window.destroy()

    edit_window = Toplevel(root)
    edit_window.title(f"Edit Cell: Row {row + 1}, Column {col_name}")
    edit_window.geometry("640x600")
    edit_window.grab_set()  # Keeps focus within the window

    text_frame = tk.Frame(edit_window)
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)

    text = Text(text_frame, wrap="word")
    text.insert("1.0", existing_content)
    text.pack(fill="both", expand=True, side="left")

    scrollbar = Scrollbar(text_frame, command=text.yview)
    scrollbar.pack(side="right", fill="y")
    text.config(yscrollcommand=scrollbar.set)

    button_frame = tk.Frame(edit_window)
    button_frame.pack(fill="x", expand=False, pady=10)  # Added pady for spacing

    save_button = tk.Button(button_frame, text="Save", command=save_edit)
    cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_edit)
    save_button.pack(side="left", padx=20, pady=5)
    cancel_button.pack(side="right", padx=20, pady=5)

    text.focus_set()  # Focuses the text widget to receive all key inputs

    # Prevent Enter key from closing the window and allow new line insertion
    def handle_return(event):
        text.insert(tk.INSERT, "\n")
        return "break"  # Stops the event from propagating further

    text.bind('<Return>', handle_return)

    edit_window.protocol("WM_DELETE_WINDOW", cancel_edit)  # Handles window close button click


# Cell Clicked
def cell_clicked(event):
    global current_cell
    row_clicked = table.get_row_clicked(event)
    col_clicked = table.get_col_clicked(event)
    current_cell = (row_clicked, col_clicked)

# Main GUI Setup
root = tk.Tk()
root.title("Webster123")
root.geometry("1000x800")

toolbar = tk.Frame(root)
toolbar.pack(side="top", fill="x", pady=10)

load_button = tk.Button(toolbar, text="Load CSV", command=load_csv)
load_button.pack(side="left", padx=5, pady=5)

save_button = tk.Button(toolbar, text="Save CSV", command=save_csv)
save_button.pack(side="left", padx=5, pady=5)

process_button = tk.Button(toolbar, text="Publish Rows to Disk", command=process_button_action)
process_button.pack(side="left", padx=5, pady=5)

open_button = tk.Button(toolbar, text="View Html Pages", command=open_button_action)
open_button.pack(side="left", padx=5, pady=5)

edit_button = tk.Button(toolbar, text="Edit Cell", command=edit_cell)
edit_button.pack(side="left", padx=5, pady=5)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, pady=10)

table = TableCanvas(frame)
# Try to disable tooltips by modifying the _tooltip attribute
if hasattr(table, '_tooltip'):
    table._tooltip.destroy()
    table._tooltip = None
table.bind("<ButtonRelease-1>", cell_clicked)
table.show()

root.mainloop()
