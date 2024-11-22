from flask import Flask, render_template_string, request, send_file, flash
import markdown
import pdfkit
import tempfile
import os
import re
import socket

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for flash messages

# Configure wkhtmltopdf
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# Your existing HTML_TEMPLATE here (no changes needed)

def sanitize_filename(filename):
    """Your existing sanitize_filename function"""
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    filename = re.sub(r'[^a-zA-Z0-9-_\s.]', '', filename)
    if not filename or filename == '.pdf':
        filename = 'document.pdf'
    return filename

def convert_markdown_to_pdf(markdown_text):
    """Updated convert_markdown_to_pdf function with better error handling"""
    temp_html = None
    temp_pdf = None
    
    try:
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
                    /* Your existing styles */
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
        
        # Create temporary files with explicit cleanup
        temp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        # Write HTML content
        with open(temp_html.name, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        # Convert to PDF with explicit configuration
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'quiet': ''
        }
        
        pdfkit.from_file(temp_html.name, temp_pdf.name, options=options, configuration=config)
        return temp_pdf.name
        
    except Exception as e:
        # Clean up files in case of error
        if temp_html and os.path.exists(temp_html.name):
            os.unlink(temp_html.name)
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        raise e

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
            except Exception as e:
                print(f"Error converting PDF: {str(e)}")
                return f"Error converting PDF: {str(e)}", 500
            finally:
                # Clean up PDF temp file after sending
                if 'pdf_path' in locals() and os.path.exists(pdf_path):
                    try:
                        os.unlink(pdf_path)
                    except Exception as e:
                        print(f"Error cleaning up PDF: {str(e)}")
    
    return render_template_string(HTML_TEMPLATE, default_text='')

if __name__ == '__main__':
    # Get local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer is running!")
    print(f"Access locally at: http://127.0.0.1:5000")
    print(f"Access from other devices at: http://{local_ip}:5000")
    print(f"Using wkhtmltopdf at: {WKHTMLTOPDF_PATH}")
    print("Make sure both devices are on the same network")
    
    app.run(host='0.0.0.0', port=5000, debug=True)