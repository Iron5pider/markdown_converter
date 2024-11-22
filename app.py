from flask import Flask, render_template_string, request, send_file
import markdown
import pdfkit
import tempfile
import os
import re

app = Flask(__name__)

# HTML template with added filename input
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Markdown to PDF Converter</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            height: 300px;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: monospace;
            resize: vertical;
        }
        .filename-input {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 0 auto;
        }
        button:hover {
            background-color: #0056b3;
        }
        .sample-text {
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Markdown to PDF Converter</h1>
        <form method="POST">
            <div class="input-group">
                <label for="filename">PDF Filename:</label>
                <input type="text" 
                       id="filename" 
                       name="filename" 
                       class="filename-input" 
                       value="document.pdf" 
                       pattern="^[a-zA-Z0-9-_\s]+\.pdf$"
                       required
                       title="Filename must end with .pdf and contain only letters, numbers, spaces, hyphens, and underscores">
            </div>
            <div class="input-group">
                <label for="markdown">Markdown Content:</label>
                <textarea id="markdown" name="markdown" placeholder="Enter your Markdown here...">{{ default_text }}</textarea>
            </div>
            <button type="submit">Convert to PDF</button>
        </form>
        <div class="sample-text">
            <p><strong>Try this sample Markdown:</strong></p>
            <pre>
# Hello World

This is a **bold** text and this is *italic*.

## List Example
- Item 1
- Item 2
- Item 3

### Code Example
```python
def hello():
    print("Hello, World!")
```</pre>
        </div>
    </div>
</body>
</html>
"""

def sanitize_filename(filename):
    """Sanitize the filename to be safe for saving"""
    # Ensure filename ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    # Remove any potentially dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9-_\s.]', '', filename)
    
    # If filename is empty after sanitization, provide a default
    if not filename or filename == '.pdf':
        filename = 'document.pdf'
    
    return filename

def convert_markdown_to_pdf(markdown_text):
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    # Add styling
    styled_html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 2em;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 4px;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 1em;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                table {{
                    border-collapse: collapse;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                th {{
                    background-color: #f4f4f4;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
    </html>
    """
    
    # Create temporary files
    temp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    
    try:
        # Write HTML content
        with open(temp_html.name, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        # Convert to PDF
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'quiet': ''
        }
        
        pdfkit.from_file(temp_html.name, temp_pdf.name, options=options)
        return temp_pdf.name
    finally:
        # Clean up HTML temp file
        os.unlink(temp_html.name)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        markdown_text = request.form['markdown']
        filename = request.form.get('filename', 'document.pdf')
        
        if markdown_text.strip():
            try:
                pdf_path = convert_markdown_to_pdf(markdown_text)
                sanitized_filename = sanitize_filename(filename)
                return send_file(
                    pdf_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=sanitized_filename
                )
            finally:
                # Clean up PDF temp file after sending
                if 'pdf_path' in locals():
                    os.unlink(pdf_path)
    
    return render_template_string(HTML_TEMPLATE, default_text='')

if __name__ == '__main__':
    # Get local IP address
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer is running!")
    print(f"Access locally at: http://127.0.0.1:5000")
    print(f"Access from other devices at: http://{local_ip}:5000")
    print("Make sure both devices are on the same network")
    
    # Run the server on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)