import pandas as pd
import sqlite3
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, Menu, font, Label, Toplevel
import webbrowser
import datetime

global_df = None  # Global variable to store the DataFrame
current_selection = None
clipboard_data = None
shift_start_row = None  # Variable to store the starting row for shift-click selection
db_file = None  # No default database file name

# Define the column order
columns = [
    "siteId", "folderPath", "ourUrl", "ourTitle", "ourContent", "Extra1", "Extra2", "topMenu",
    "ourHeader", "ourFooter", "styleSheet", "scriptsUrl", "fileExtension", "ourMeta", "shareImageUrl",
    "Website", "websiteUrl", "Icon", "topHtml", "headTag", "ourShareButton", "useLinkBox", "directoryMode", "frontPage"
]

# Define initial values
initial_data = {
    "ourUrl": ["double-clk-to-edit"],
    "folderPath": ["c:\\webster123"],
    "fileExtension": ["html"],
    "scriptsUrl": [""],
    "ourTitle": [""],
    "ourContent": [f"""<center><h2>Congratulations!</h2><p>You've published your first page. <br>Change it to your html to get started.<br>This is Webster123pro v1.0.5<br>Visit <a href="https://webster123.com/">Webster123.com</a> for instructions.</p></center>"""],
    "Extra1": [""],
    "Extra2": [""],
    "siteId": ["My Site"],
    "topMenu": [""],
    "ourHeader": [f"""<img src="https://webster123.com/webster-logo-web.jpg">"""],
    "ourFooter": [""],
    "directoryMode": ["False"],
    "shareImageUrl": [""],
    "ourMeta": [""],
    "Website": [""],
    "websiteUrl": [""],
    "styleSheet": [""],
    "Icon": [""],
    "topHtml": [""],
    "headTag": [""],
    "ourShareButton": [""],
    "useLinkBox": ["False"],
    "frontPage": ["False"]
}

# Add 20 extra empty rows
for _ in range(20):
    for key in initial_data.keys():
        initial_data[key].append("")

# Column configuration
column_config = {
    "ourUrl": {"width": 220, "instructions": "Words with a dash between them, no special characters"},
    "folderPath": {"width": 100, "instructions": "The folder on your local where you wish to store the pages you create. Like C:\\webster123"},
    "fileExtension": {"width": 100, "instructions": "html or php"},
    "ourTitle": {"width": 100, "instructions": "The title of your web page."},
    "ourContent": {"width": 100, "instructions": "Html content"},
    "Extra1": {"width": 100, "instructions": "Extra Html content"},
    "Extra2": {"width": 100, "instructions": "Extra Html content"},
    "siteId": {"width": 100, "instructions": "Your site Id, Which site is this?"},
    "topMenu": {"width": 100, "instructions": "Our menu entries are Anchor links stacked on top of each other."},
    "ourHeader": {"width": 100, "instructions": "Html for the header of the website."},
    "ourFooter": {"width": 100, "instructions": "Html for the Footer of our site."},
    "directoryMode": {"width": 100, "instructions": "False and we produce a url like example.html. True and we create a folder example/ and put an index page in it.."},
    "shareImageUrl": {"width": 100, "instructions": "The url of your share image"},
    "ourMeta": {"width": 100, "instructions": "The meta Description of your page."},
    "Website": {"width": 100, "instructions": "yoursite.com"},
    "websiteUrl": {"width": 100, "instructions": "Website URL. Must have trailing slash '/', like https://yoursite.com/"},
    "styleSheet": {"width": 100, "instructions": "The url of your stylesheet file. On your local drive it can look like file:///c:/Stylesheets/mystylesheet.css This way you can work with a stylesheet on your drive. When you publish the page on the internet, you can change it to something like https://mysite.com/mystylesheet.css"},
    "Icon": {"width": 100, "instructions": "The website icon, usually 100x100px"},
    "topHtml": {"width": 100, "instructions": "Inserted after <html>"},
    "headTag": {"width": 100, "instructions": "Inserted after <head>"},
    "ourShareButton": {"width": 100, "instructions": "AddtoAny Share Button. Leave blank to not use."},
    "useLinkBox": {"width": 100, "instructions": "If True, a Link To This Page Box will be added"},
    "scriptsUrl": {"width": 100, "instructions": "The url of your java script file. On your local drive it can look like file:///c:/Scriptsfolder/myscript.js This way you can work with a script on your drive. When you publish the page on the internet, you can change it to something like https://mysite.com/myscript.js"}
}

# Add visual settings
def set_visual_settings(root):
    root.configure(bg="#f0f0f0")  # Background color of the main window

def set_font_settings():
    return font.Font(family="Arial", size=10, weight="normal", slant="roman")

# Undo/Redo Manager
class UndoRedoManager:
    def __init__(self):
        self.history = []
        self.redo_stack = []
        self.current_state = None

    def save_state(self, state):
        if self.current_state is not None:
            self.history.append(self.current_state)
        self.current_state = state.copy()
        self.redo_stack.clear()

    def undo(self):
        if self.history:
            self.redo_stack.append(self.current_state)
            self.current_state = self.history.pop()
            return self.current_state
        return None

    def redo(self):
        if self.redo_stack:
            self.history.append(self.current_state)
            self.current_state = self.redo_stack.pop()
            return self.current_state
        return None

undo_manager = UndoRedoManager()

class SimpleTable(tk.Canvas):
    def __init__(self, parent, rows=10, cols=5, font_size=12):
        super().__init__(parent)
        self.parent = parent
        self.rows = rows
        self.cols = cols
        self.cells = {}
        self.headers = []
        self.row_numbers = []
        self.header_height = 30
        self.row_number_width = 50
        self.font_size = font_size
        self.font = set_font_settings()
        self.cell_height = self.font.metrics("linespace") + 10

        self.selection_rects = []
        self.start_row = None
        self.edit_window = None  # Track the edit window
        self.clipboard_data = None  # To store single cell value for pasting

        self.header_canvas = tk.Canvas(parent, height=self.header_height, bg='lightblue')
        self.row_number_canvas = tk.Canvas(parent, width=self.row_number_width, bg='lightblue')

        self.header_canvas.grid(row=0, column=1, sticky='ew')
        self.row_number_canvas.grid(row=1, column=0, sticky='ns')

        self.create_widgets()
        self.bind_shortcuts()

    def create_widgets(self):
        self.config(bg='white', highlightthickness=0)
        self.bind("<Button-1>", self.on_table_click)
        self.bind("<B1-Motion>", self.on_table_drag)
        self.bind("<ButtonRelease-1>", self.on_drag_end)
        self.bind("<Double-1>", self.on_table_double_click)
        self.bind("<Button-3>", self.on_table_right_click)
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.row_number_canvas.bind("<Button-3>", self.on_row_number_right_click)
        self.xview_moveto(0)
        self.yview_moveto(0)

    def bind_shortcuts(self):
        self.parent.bind("<Control-c>", self.copy_selection)
        self.parent.bind("<Control-x>", self.cut_selection)
        self.parent.bind("<Control-v>", self.paste_selection)
        self.parent.bind("<Control-z>", self.undo)
        self.parent.bind("<Control-y>", self.redo)

    def cut_selection(self):
        self.copy_selection()
        self.delete_selection(current_selection[0], current_selection[1])

    def create_cell(self, row, col, value):
        col_name = self.headers[col]
        cell_config = column_config.get(col_name, {"width": 100, "instructions": ""})
        cell_width = cell_config["width"]
        x0 = self.row_number_width + sum(column_config.get(self.headers[c], {"width": 100})["width"] for c in range(col))
        y0 = row * self.cell_height
        x1 = x0 + cell_width
        y1 = y0 + self.cell_height
        rect = self.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
        
        # Calculate the number of characters that fit in the cell width
        char_width = self.font.measure("A")
        max_chars = cell_width // char_width
        display_value = str(value)[:max_chars] if value else ""
        
        text = self.create_text(x0 + 5, y0 + 5, anchor="nw", text=display_value, width=cell_width - 10, font=self.font, tag=f"cell_{row}_{col}")
        self.cells[(row, col)] = (rect, text)

    def create_headers(self):
        self.header_canvas.delete("all")
        x_offset = 0
        for col, header in enumerate(self.headers):
            cell_config = column_config.get(header, {"width": 100, "instructions": ""})
            cell_width = cell_config["width"]
            x0 = x_offset
            y0 = 0
            x1 = x0 + cell_width
            y1 = y0 + self.header_height
            self.header_canvas.create_rectangle(x0, y0, x1, y1, fill="lightblue", outline="black")
            self.header_canvas.create_text(x0 + 5, y0 + 5, anchor="nw", text=header, font=self.font)
            x_offset += cell_width

    def create_row_numbers(self):
        self.row_number_canvas.delete("all")
        for row in range(self.rows):
            x0 = 0
            y0 = row * self.cell_height
            x1 = x0 + self.row_number_width
            y1 = y0 + self.cell_height
            rect = self.row_number_canvas.create_rectangle(x0, y0, x1, y1, fill="lightblue", outline="black")
            text = self.row_number_canvas.create_text(x0 + 5, y0 + 5, anchor="nw", text=str(row + 1), font=self.font)
            self.row_numbers.append((rect, text))
            self.row_number_canvas.tag_bind(rect, "<Button-1>", lambda event, r=row: self.on_row_number_click(event, r))
            self.row_number_canvas.tag_bind(text, "<Button-1>", lambda event, r=row: self.on_row_number_click(event, r))

    def on_row_number_click(self, event, row):
        global shift_start_row
        if shift_start_row is None or not event.state & 0x1:  # If shift key is not pressed
            shift_start_row = row
        self.clear_selection()
        self.highlight_rows(shift_start_row, row)
        global current_selection
        current_selection = (min(shift_start_row, row), 0, max(shift_start_row, row), self.cols - 1)

    def highlight_rows(self, start_row, end_row):
        for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for col in range(self.cols):
                self.highlight_cell(row, col)

    def load_data(self, data, column_names):
        self.rows = len(data)
        self.cols = len(data[0]) if self.rows > 0 else 0
        self.headers = column_names
        self.cells.clear()
        self.delete("all")
        self.populate_table()
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.create_cell(row, col, value)
        self.update_idletasks()
        self.config(scrollregion=self.bbox("all"))
        self.create_headers()
        self.create_row_numbers()
        self.update_scroll_region()

    def populate_table(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.create_cell(row, col, "")
        self.create_headers()
        self.create_row_numbers()

    def on_table_click(self, event):
        global current_selection
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        row, col = int(y // self.cell_height), self.get_col_at_x(x - self.row_number_width)
        if row >= 0 and col >= 0:
            self.clear_selection()
            self.highlight_cell(row, col)
            current_selection = (row, col, row, col)

    def get_col_at_x(self, x):
        x_offset = 0
        for col, header in enumerate(self.headers):
            cell_config = column_config.get(header, {"width": 100, "instructions": ""})
            cell_width = cell_config["width"]
            if x_offset <= x < x_offset + cell_width:
                return col
            x_offset += cell_width
        return -1

    def on_table_drag(self, event):
        global current_selection
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        row, col = int(y // self.cell_height), self.get_col_at_x(x - self.row_number_width)
        if row >= 0 and col >= 0 and current_selection is not None:
            self.clear_selection()
            row1, col1, row2, col2 = current_selection
            current_selection = (row1, col1, row, col)
            self.highlight_rectangle(row1, col1, row, col)

    def on_drag_end(self, event):
        self.start_row = None

    def on_table_double_click(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        row, col = int(y // self.cell_height), self.get_col_at_x(x - self.row_number_width)
        if row >= 0 and col >= 0:
            self.edit_cell(row, col)

    def on_table_right_click(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        row, col = int(y // self.cell_height), self.get_col_at_x(x - self.row_number_width)
        if row >= 0 and col >= 0:
            self.show_cell_context_menu(event, row, col)

    def on_row_number_right_click(self, event):
        y = self.row_number_canvas.canvasy(event.y)
        row = int(y // self.cell_height)
        if row >= 0:
            self.show_row_context_menu(event, row)

    def on_mouse_wheel(self, event):
        if event.state & 0x1:  # If Shift key is pressed
            self.xview_scroll(-1 * int((event.delta / 120)), "units")
        else:
            self.yview_scroll(-1 * int((event.delta / 120)), "units")
        self.update_scroll_region()

    def highlight_cell(self, row, col):
        self.itemconfig(self.cells[(row, col)][0], fill="lightyellow")
        self.itemconfig(self.cells[(row, col)][1], fill="darkblue", font=self.font)

    def clear_selection(self):
        for rect in self.selection_rects:
            self.delete(rect)
        self.selection_rects.clear()
        for (row, col), (rect, text) in self.cells.items():
            self.itemconfig(rect, fill="white")
            self.itemconfig(text, fill="black", font=self.font)

    def highlight_rectangle(self, row1, col1, row2, col2):
        for row in range(min(row1, row2), max(row1, row2) + 1):
            for col in range(min(col1, col2), max(col1, col2) + 1):
                self.highlight_cell(row, col)
                cell_config = column_config.get(self.headers[col], {"width": 100, "instructions": ""})
                cell_width = cell_config["width"]
                x0 = self.row_number_width + sum(column_config.get(self.headers[c], {"width": 100})["width"] for c in range(col))
                y0 = row * self.cell_height
                x1 = x0 + cell_width
                y1 = y0 + self.cell_height
                rect = self.create_rectangle(x0, y0, x1, y1, outline="blue", width=2)
                self.selection_rects.append(rect)

    def show_cell_context_menu(self, event, row, col):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Copy Selection", command=self.copy_selection)
        menu.add_command(label="Paste Selection", command=self.paste_selection)
        menu.add_command(label="Delete Selection", command=lambda: self.delete_selection(row, col))
        menu.post(event.x_root, event.y_root)

    def show_row_context_menu(self, event, row):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Insert Row", command=lambda: self.insert_row(row))
        menu.add_command(label="Delete Row", command=lambda: self.delete_row(row))
        menu.add_command(label="Copy Selection", command=self.copy_selection)
        menu.add_command(label="Publish Selected Rows", command=self.publish_selected_rows)
        menu.add_command(label="View Selected Rows", command=self.view_selected_rows)
        menu.post(event.x_root, event.y_root)

    def insert_row(self, row):
        global global_df
        new_row = [""] * self.cols
        global_df = pd.concat([global_df.iloc[:row], pd.DataFrame([new_row], columns=global_df.columns), global_df.iloc[row:]]).reset_index(drop=True)
        undo_manager.save_state(global_df.copy())
        update_table()

    def delete_row(self, row):
        global global_df
        global_df = global_df.drop(global_df.index[row]).reset_index(drop=True)
        undo_manager.save_state(global_df.copy())
        update_table()

    def delete_selection(self, row, col):
        global global_df, current_selection
        if current_selection is not None:
            row1, col1, row2, col2 = current_selection
            global_df.iloc[min(row1, row2):max(row1, row2) + 1, min(col1, col2):max(col1, col2) + 1] = ""
            undo_manager.save_state(global_df.copy())
            update_table()

    def copy_selection(self):
        global global_df, clipboard_data, current_selection
        if current_selection is not None:
            row1, col1, row2, col2 = current_selection
            if row1 == row2 and col1 == col2:
                # Copy a single cell
                clipboard_data = global_df.iat[row1, col1]
            else:
                # Copy a range of cells
                clipboard_data = global_df.iloc[min(row1, row2):max(row1, row2) + 1, min(col1, col2):max(col1, col2) + 1].copy()

    def paste_selection(self):
        global global_df, clipboard_data, current_selection
        if clipboard_data is not None and current_selection is not None:
            row1, col1, row2, col2 = current_selection
            if isinstance(clipboard_data, pd.DataFrame):
                rows_to_paste = clipboard_data.shape[0]
                cols_to_paste = clipboard_data.shape[1]
                if row1 + rows_to_paste > self.rows or col1 + cols_to_paste > self.cols:
                    messagebox.showerror("Paste Error", "Not enough space to paste the selection")
                    return
                for i in range(rows_to_paste):
                    for j in range(cols_to_paste):
                        global_df.iat[row1 + i, col1 + j] = clipboard_data.iat[i, j]
            else:
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        global_df.iat[row, col] = clipboard_data
            undo_manager.save_state(global_df.copy())
            update_table()

    def undo(self, event=None):
        global global_df
        state = undo_manager.undo()
        if state is not None:
            global_df = state.copy()
            update_table()

    def redo(self, event=None):
        global global_df
        state = undo_manager.redo()
        if state is not None:
            global_df = state.copy()
            update_table()

    def edit_cell(self, row, col):
        if self.edit_window is not None and self.edit_window.winfo_exists():
            self.edit_window.lift()  # Bring the existing edit window to the front
            return
        if (row, col) not in self.cells:
            return
        full_text = global_df.iat[row, col] if not pd.isna(global_df.iat[row, col]) else ""  # Handle NaN values
        col_name = self.headers[col]
        cell_config = column_config.get(col_name, {"width": 100, "instructions": ""})
        instructions = cell_config.get("instructions", "")

        self.edit_window = tk.Toplevel(self)
        self.edit_window.title(f"Edit Cell ({row, col})")

        if instructions:
            instruction_label = tk.Label(self.edit_window, text=instructions, wraplength=400, justify="left")
            instruction_label.pack(fill="x", padx=10, pady=10)

        text_frame = tk.Frame(self.edit_window, padx=10, pady=10)
        text_frame.pack(fill="both", expand=True)

        text = Text(text_frame, wrap="word")
        text.insert("1.0", full_text)
        text.pack(fill="both", expand=True, side="left")

        scrollbar = Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.config(yscrollcommand=scrollbar.set)

        text.bind_all("<MouseWheel>", lambda event: text.yview_scroll(-1 * int((event.delta / 120)), "units"))

        button_frame = tk.Frame(self.edit_window)
        button_frame.pack(fill="x", expand=False, pady=10)

        def save_edit():
            new_text = text.get("1.0", tk.END).strip()
            self.itemconfig(self.cells[(row, col)][1], text=new_text[:cell_config["width"] // self.font.measure("A")])  # Update with truncated text
            global_df.iat[row, col] = new_text  # Update the global DataFrame with full text
            undo_manager.save_state(global_df.copy())  # Save the state for undo
            self.edit_window.destroy()
            self.edit_window = None
            self.update_scroll_region()  # Update the scroll region after editing

        save_button = tk.Button(button_frame, text="Save", command=save_edit)
        cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: [self.edit_window.destroy(), setattr(self, 'edit_window', None)])
        save_button.pack(side="left", padx=20, pady=5)
        cancel_button.pack(side="right", padx=20, pady=5)

        text.focus_set()

        def handle_return(event):
            text.insert(tk.INSERT, "\n")
            return "break"

        text.bind('<Return>', handle_return)

        # Update the scroll region after closing the edit window
        self.edit_window.bind("<Destroy>", lambda event: [self.update_scroll_region(), setattr(self, 'edit_window', None)])

    def update_scroll_region(self):
        self.config(scrollregion=self.bbox("all"))
        self.header_canvas.config(scrollregion=self.header_canvas.bbox("all"))
        self.row_number_canvas.config(scrollregion=self.row_number_canvas.bbox("all"))

        if self.xview() is not None:
            self.header_canvas.xview_moveto(self.xview()[0])
        if self.yview() is not None:
            self.row_number_canvas.yview_moveto(self.yview()[0])

        # Ensure headers and row numbers are always visible
        self.tag_lower("header")
        self.tag_lower("row_num")
        self.parent.update()

        # Re-bind scroll events
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def xview_handler(self, *args):
        self.xview_moveto = super().xview_moveto
        self.xview_scroll = super().xview_scroll
        self.xview(*args)
        self.header_canvas.xview(*args)
        self.update_scroll_region()

    def yview_handler(self, *args):
        self.yview_moveto = super().yview_moveto
        self.yview_scroll = super().yview_scroll
        self.yview(*args)
        self.row_number_canvas.yview(*args)
        self.update_scroll_region()

    def publish_selected_rows(self):
        global current_selection
        if current_selection is not None:
            row1, col1, row2, col2 = current_selection
            rows_to_publish = list(range(min(row1, row2) + 1, max(row1, row2) + 2))
            result = publish_rows_to_disk(",".join(map(str, rows_to_publish)))
            messagebox.showinfo("Publish Result", result)

    def view_selected_rows(self):
        global current_selection
        if current_selection is not None:
            row1, col1, row2, col2 = current_selection
            rows_to_view = list(range(min(row1, row2) + 1, max(row1, row2) + 2))
            result = view_html_pages(",".join(map(str, rows_to_view)))
            messagebox.showinfo("View Result", result)

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
        link_box_html = f"""<br><b><center>The button below can help educators and others link to this page:</center></b><br><div style="width: 200px; margin: 0 auto;">
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

    return f"""<html>
{check_nan(row['topHtml'])}
<head>
    <title>{check_nan(row['ourTitle'])}</title>
    <meta name="description" content="{check_nan(row['ourMeta'])}">
    <meta charset="UTF-8">
    <script src="{check_nan(row['scriptsUrl'])}"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="{canonical_url}">
    <link rel="icon" href="{check_nan(row['Icon'])}" sizes="32x32">
    <link rel="stylesheet" href="{check_nan(row['styleSheet'])}">
    <meta property="og:title" content="{check_nan(row['ourTitle'])}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{check_nan(row['shareImageUrl'])}">
    <meta property="og:description" content="{check_nan(row['ourTitle'])}">
    {check_nan(row['headTag'])}
</head>
<body>
    <div class="header">{check_nan(row['ourHeader'])}</div>
    <div class="topnav" id="myTopnav">{check_nan(row['topMenu'])}<a href="javascript:void(0);" style="font-size:15px;" class="icon" onclick="myFunction()">&#9776;</a></div>
    <div class="content">
        <h2>{check_nan(row['ourTitle'])}</h2>
        {full_content}
        {link_box_html}
        {check_nan(row['ourShareButton'])}
    </div>
    <div class="footer">{check_nan(row['ourFooter'])}</div>  
    
    <script>
        function myFunction() {{
            var x = document.getElementById("myTopnav");
            if (x.className === "topnav") {{
                x.className += " responsive";
            }} else {{
                x.className = "topnav";
            }}
        }}
    </script>
</body>
</html>"""

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
        global_df = pd.read_csv(file_path, encoding='utf-8')
        save_to_db(global_df)  # Save the data to the database
        
        # Ensure columns are in the predefined order
        global_df = global_df.reindex(columns=columns)
        
        # Add extra empty rows if necessary to make sure there are at least 21 rows
        if len(global_df) < 21:
            extra_rows = 21 - len(global_df)
            empty_rows = pd.DataFrame({col: [""] * extra_rows for col in columns})
            global_df = pd.concat([global_df, empty_rows], ignore_index=True)
        
        update_table()
    except UnicodeDecodeError:
        messagebox.showerror("Load Error", "Failed to load CSV: The file is not in UTF-8 encoding.")
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load CSV: {str(e)}")

# Update Table
def update_table(rows_to_display=None):
    global global_df
    if global_df is not None:
        if rows_to_display is not None:
            data = global_df.head(rows_to_display).fillna("").values.tolist()
        else:
            data = global_df.fillna("").values.tolist()
        column_names = global_df.columns.tolist()
        table.load_data(data, column_names)
        table.update_scroll_region()

# Save DataFrame to SQLite
def save_to_db(df):
    global db_file
    if db_file is None:
        messagebox.showinfo("Welcome to Webster123", "To get started you must create your first database. Click File/Backup Database to save the table shown as your first database or click File/Open to open an existing database.")
        return

    try:
        conn = sqlite3.connect(db_file)
        df.to_sql('pages', conn, if_exists='replace', index=False)
        conn.close()
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save to database: {str(e)}")

# Commit changes to the database
def commit_changes():
    backup_current_db()  # Backup the current database before committing changes
    global global_df
    save_to_db(global_df)
    messagebox.showinfo("Commit Successful", "Changes have been committed to the database.")

# Function to backup the current database
def backup_current_db():
    global db_file
    if db_file and os.path.exists(db_file):
        backup_db_file = db_file.replace(".db", f"_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        os.rename(db_file, backup_db_file)
        messagebox.showinfo("Backup Created", f"Current database backed up as {backup_db_file}")

# Function to update the database filename display
def update_db_filename_display():
    global db_file
    db_filename_label.config(text=f"DB File: {os.path.basename(db_file)}" if db_file else "No DB File")

# Load DataFrame from SQLite
def load_from_db(file):
    conn = sqlite3.connect(file)
    df = pd.read_sql_query("SELECT * FROM pages", conn)
    conn.close()
    return df

# Save As functionality
def save_as():
    global db_file
    initial_db_name = db_file if db_file else "database.db"
    new_file = filedialog.asksaveasfilename(initialfile=initial_db_name, defaultextension=".db", filetypes=[("Database Files", "*.db")])
    if new_file:
        db_file = new_file
        backup_and_save_db(new_file)
        update_db_filename_display()  # Update the label when saving as

def backup_and_save_db(new_file):
    global db_file
    if db_file and os.path.exists(db_file):
        backup_db_file = db_file.replace(".db", f"_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        os.rename(db_file, backup_db_file)
        messagebox.showinfo("Backup Created", f"Existing database backed up as {backup_db_file}")
    db_file = new_file
    save_to_db(global_df)

# Export DataFrame to CSV
def export_csv():
    global global_df
    if global_df is None:
        messagebox.showwarning("No Data", "No data available to export. Please load data first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        global_df.to_csv(file_path, index=False)
        messagebox.showinfo("CSV Exported", f"CSV file exported successfully to {file_path}.")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export CSV: {str(e)}")

# Import CSV
def import_csv():
    global global_df, db_file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        messagebox.showwarning("Import Error", "No file selected.")
        return

    response = messagebox.askokcancel(
        "Import CSV",
        "You are importing a CSV file. Click Continue to save it as a database. "
        "If you select an existing database, a dated backup will be made.",
        icon='warning'
    )

    if not response:
        return

    try:
        
        global_df = pd.read_csv(file_path, encoding='utf-8')
        

        # Ensure columns are in the predefined order
        global_df = global_df.reindex(columns=columns)

        # Add extra empty rows if necessary to make sure there are at least 21 rows
        if len(global_df) < 21:
            extra_rows = 21 - len(global_df)
            empty_rows = pd.DataFrame({col: [""] * extra_rows for col in columns})
            global_df = pd.concat([global_df, empty_rows], ignore_index=True)

        # Prompt to save as DB with the same name and a .db extension
        initial_db_name = os.path.splitext(os.path.basename(file_path))[0] + ".db"
        db_file = filedialog.asksaveasfilename(initialfile=initial_db_name, defaultextension=".db", filetypes=[("Database Files", "*.db")])

        if db_file:
            # Back up the existing database if it exists
            backup_and_save_db(db_file)
            update_table()
        else:
            messagebox.showwarning("Save Error", "Database file not specified. Data not saved.")
    except UnicodeDecodeError:
        messagebox.showerror("Import Error", "Failed to import CSV: The file is not in UTF-8 encoding.")
    except Exception as e:
        
        messagebox.showerror("Import Error", f"Failed to import CSV: {str(e)}")

# Open DB
def open_db():
    global global_df, db_file
    file_path = filedialog.askopenfilename(filetypes=[("Database Files", "*.db")])
    if not file_path:
        return
    db_file = file_path
    try:
        global_df = load_from_db(db_file)
        undo_manager.save_state(global_df.copy())  # Save the initial state for undo
        update_table()
        update_db_filename_display()  # Update the label when opening a db
        messagebox.showinfo("Open Successful", f"Database {db_file} opened successfully.")
    except Exception as e:
        messagebox.showerror("Open Error", f"Failed to open database: {str(e)}")

# Save Whole Database Confirmation
def save_db_with_confirmation():
    global db_file
    response = messagebox.askokcancel(
        "Save Database",
        "Your edits have already been saved to the database. "
        "There is no need to save the whole database unless you want to back it up or move it. "
        "Before it is saved or moved, the program will back it up. Continue?",
        icon='warning'
    )
    if response:
        save_as()

# Initialize the SQLite database (if needed)
def init_db():
    if db_file:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                siteId TEXT,
                folderPath TEXT,
                ourUrl TEXT,
                ourTitle TEXT,
                ourContent TEXT,
                Extra1 TEXT,
                Extra2 TEXT,
                topMenu TEXT,
                ourHeader TEXT,
                ourFooter TEXT,
                styleSheet TEXT,
                scriptsUrl TEXT,
                fileExtension TEXT,
                ourMeta TEXT,
                shareImageUrl TEXT,
                Website TEXT,
                websiteUrl TEXT,
                Icon TEXT,
                topHtml TEXT,
                headTag TEXT,
                ourShareButton TEXT,
                useLinkBox TEXT,
                directoryMode TEXT,
                frontPage TEXT
            )
        ''')
        conn.commit()
        conn.close()

# Welcome Window
def show_welcome_window():
    welcome_window = Toplevel(root)
    welcome_window.title("Welcome to Webster123pro")
    welcome_window.geometry("400x200")
    welcome_window.configure(bg="#f0f0f0")

    welcome_label = Label(welcome_window, text="Welcome to Webster123pro!", font=("Arial", 14), bg="#f0f0f0")
    welcome_label.pack(pady=10)

    create_db_button = tk.Button(welcome_window, text="Create Database", command=lambda: create_database(welcome_window))
    create_db_button.pack(pady=10)

    open_db_button = tk.Button(welcome_window, text="Open Database", command=lambda: open_database(welcome_window))
    open_db_button.pack(pady=10)

def create_database(welcome_window):
    global global_df, db_file
    db_file = filedialog.asksaveasfilename(initialfile="Startup.db", defaultextension=".db", filetypes=[("Database Files", "*.db")])
    if db_file:
        global_df = pd.DataFrame(initial_data, columns=columns)
        save_to_db(global_df)
        undo_manager.save_state(global_df.copy())  # Save the initial state for undo
        update_db_filename_display()
        update_table()
        welcome_window.destroy()

def open_database(welcome_window):
    open_db()
    welcome_window.destroy()

# Main GUI Setup
root = tk.Tk()
root.title("Webster123pro")
root.geometry("1200x600")
set_visual_settings(root)

# Create the menu bar
menubar = Menu(root)
root.config(menu=menubar)

# Create the File menu
file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_db)
file_menu.add_command(label="Backup Database", command=save_as)  # Relabel Save As to Backup Database
file_menu.add_command(label="Commit Changes to Database", command=commit_changes)  # Add Commit Changes to Database
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Create the Edit menu
edit_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Export as CSV (UTF-8)", command=export_csv)
edit_menu.add_command(label="Import CSV (UTF-8)", command=import_csv)

# Add a label to display the database file name at the same level as the menu
menubar_frame = tk.Frame(root, bg="#dcdcdc")
menubar_frame.pack(side="top", fill="x")

db_filename_label = Label(menubar_frame, text="No DB File", anchor='e', bg="#dcdcdc")
db_filename_label.pack(side="right")

toolbar = tk.Frame(root, bg="#dcdcdc")
toolbar.pack(side="top", fill="x", pady=10)

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(fill="both", expand=True, pady=10)

x_scrollbar = tk.Scrollbar(frame, orient="horizontal")
x_scrollbar.grid(row=2, column=1, sticky='ew')

y_scrollbar = tk.Scrollbar(frame, orient="vertical")
y_scrollbar.grid(row=1, column=2, sticky='ns')

# Use the SimpleTable class to create a custom table
table = SimpleTable(frame)
table.grid(row=1, column=1, sticky='nsew')

# Configure scrollbars
x_scrollbar.config(command=table.xview_handler)
y_scrollbar.config(command=table.yview_handler)
table.config(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

# Configure grid weights to make the table expandable
frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(1, weight=1)

# Display the welcome window
root.after(100, show_welcome_window)  # Show welcome window after the main window is initialized
# 1000
#lines
#we
#made
#it!....confetti falls....applause and cheers. Thank you ChatGPT4o

root.mainloop()
