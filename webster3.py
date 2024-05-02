import gradio as gr
import pandas as pd
import os
import webbrowser

global_df = None  # Global variable to store the DataFrame
global_files_to_open = []  # Global list to store file paths for opening in browser

def ensure_dir(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def write_html(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def process_and_save(line_numbers):
    global global_df
    global global_files_to_open

    if global_df is None:
        return "No CSV loaded. Please load a CSV file first."

    try:
        lines_to_process = parse_line_numbers(line_numbers)
        output = []
        global_files_to_open = []  # Clear previous list

        for index in lines_to_process:
            if index < len(global_df):
                row = global_df.iloc[index]
                folder_path = row['folderPath']
                
                # Handle directoryMode with flexibility for string representations
                directory_mode = row.get('directoryMode', 'false')  # Default to 'false' if not specified
                if isinstance(directory_mode, bool):
                    directory_mode = 'true' if directory_mode else 'false'
                else:
                    directory_mode = directory_mode.strip().lower()  # Convert to lower case and strip whitespaces
                
                # Determine the file path based on directoryMode
                if directory_mode == "true":
                    file_name = os.path.join(row['ourUrl'], "index")
                else:
                    file_name = row['ourUrl']
                
                file_extension = row.get('fileExtension', 'html')  # Default to .html if not specified
                full_path = os.path.join(folder_path, f"{file_name}.{file_extension}")
                
                ensure_dir(os.path.dirname(full_path))
                html_content = generate_html_content(row)
                write_html(html_content, full_path)
                output.append(f"Processed row {index} and saved to {full_path}")
                global_files_to_open.append(full_path)

        return "\n".join(output)

    except Exception as e:
        return f"Error processing data: {str(e)}"




def open_in_browser():
    if not global_files_to_open:
        return "No files to open. Please process data first."
    for file in global_files_to_open:
        webbrowser.open(f"file://{os.path.abspath(file)}", new=2)
    return f"Opened {len(global_files_to_open)} files in the browser."

def generate_html_content(row):
    # Check each field and replace NaN with an empty string
    def check_nan(value):
        return "" if pd.isna(value) else value

    # Concatenate ourContent, Extra1, and Extra2 with NaN checks
    full_content = f"{check_nan(row['ourContent'])}{check_nan(row.get('Extra1', ''))}{check_nan(row.get('Extra2', ''))}"
    
    # Handle directoryMode and frontPage with flexibility for string representations
    directory_mode = check_nan(row.get('directoryMode', 'false'))
    front_page = check_nan(row.get('frontPage', 'false'))
    
    if isinstance(directory_mode, bool):
        directory_mode = 'true' if directory_mode else 'false'
    else:
        directory_mode = directory_mode.strip().lower()

    if isinstance(front_page, bool):
        front_page = 'true' if front_page else 'false'
    else:
        front_page = front_page.strip().lower()

    # Determine the canonical URL based on directoryMode and frontPage
    if front_page == "true" and directory_mode != "true":
        canonical_url = row['websiteUrl']
    elif directory_mode == "true":
        canonical_url = f"{row['websiteUrl']}{row['ourUrl']}/"
    else:
        file_extension = row.get('fileExtension', 'html')
        canonical_url = f"{row['websiteUrl']}{row['ourUrl']}.{file_extension}"

    # Handle useLinkBox
    use_link_box = check_nan(row.get('useLinkBox', 'false'))
    if isinstance(use_link_box, bool):
        use_link_box = 'true' if use_link_box else 'false'
    else:
        use_link_box = use_link_box.strip().lower()

    link_box_html = ""
    if use_link_box == "true":
        link_box_html = f"""
        <div style="width: 200px; margin: 0 auto;">
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
        </script>
        """

    # Retrieve topHtml and headTag from the row with NaN checks
    top_html = check_nan(row.get('topHtml', ''))
    head_tag = check_nan(row.get('headTag', ''))

    # Return the complete HTML document
    return f"""
    <html>
    {top_html}
    <head>
        <title>{check_nan(row['ourTitle'])}</title>
        <meta name="description" content="{check_nan(row['ourMeta'])}">
        <link rel="canonical" href="{canonical_url}">
        <link rel="icon" href="{check_nan(row['Icon'])}" sizes="32x32">
        <link rel="stylesheet" href="{check_nan(row['styleSheet'])}">
        {head_tag}
        <meta property="og:title" content="{check_nan(row['ourTitle'])}">
        <meta property="og:url" content="{canonical_url}">
        <meta property="og:image" content="{check_nan(row['shareImageUrl'])}">
        <meta property="og:description" content="{check_nan(row['ourTitle'])}">
    </head>
    <body>
        <div class="header">{check_nan(row['ourHeader'])}</div>
        <div class="topnav" id="myTopnav">{check_nan(row['topMenu'])}</div>
        <div class="content">
            <h2>{check_nan(row['ourTitle'])}</h2>
            {full_content}
            {link_box_html}
            {check_nan(row['ourShareButton'])}
        </div>
        <div class="footer">{check_nan(row['ourFooter'])}</div>
    </body>
    </html>
    """





# The remaining parts of your app setup and function definitions remain unchanged.



def parse_line_numbers(line_numbers):
    """
    Parses a string of line numbers and ranges into a list of individual line numbers.
    Expects line numbers in the format "1,2,5-7,10" and returns [1, 2, 5, 6, 7, 10].
    Also handles single line inputs like "3".
    """
    result = []
    parts = line_numbers.split(',')
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))  # Ensure single numbers are handled
    return result

def load_csv(file):
    global global_df
    try:
        global_df = pd.read_csv(file)
        return global_df  # Update the display DataFrame
    except Exception as e:
        return f"Failed to load CSV: {str(e)}"

with gr.Blocks() as app:
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload CSV File")
            # Update the label to "Rows to Process"
            row_input = gr.Textbox(label="Rows to Process (e.g., 0-2,4,6-8)")
            process_button = gr.Button("Process and Save Data")
            open_button = gr.Button("Open HTML Pages")
        with gr.Column(scale=1):
            output_area = gr.Textbox(label="Output", lines=10)
    with gr.Row():
        df_component = gr.Dataframe()

    file_input.change(load_csv, inputs=file_input, outputs=df_component)
    process_button.click(process_and_save, inputs=row_input, outputs=output_area)
    open_button.click(open_in_browser, outputs=output_area)

app.launch()