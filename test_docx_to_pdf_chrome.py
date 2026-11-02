# -*- coding: utf-8 -*-
"""
Test converting docx to HTML with mammoth, styling with CSS, and printing to PDF using Chrome.
"""

import os
import subprocess
import mammoth

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def test_convert():
    docx_file = r"d:\dsp\LeTanDung_24150654\LeTanDung_24150654.docx"
    with open(docx_file, "rb") as f:
        result = mammoth.convert_to_html(f)
        html_body = result.value
        
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 20mm 20mm 20mm 30mm;
}}
body {{
    font-family: 'Times New Roman', serif;
    font-size: 13pt;
    line-height: 1.3;
    text-align: justify;
    color: #000;
}}
h1 {{
    font-size: 16pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 18pt;
    margin-bottom: 6pt;
    page-break-before: always;
}}
h2 {{
    font-size: 14pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 4pt;
}}
h3 {{
    font-size: 13pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 6pt;
    margin-bottom: 2pt;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 11pt;
}}
th, td {{
    border: 1px solid #ccc;
    padding: 4pt 6pt;
}}
th {{
    background-color: #f2f2f2;
    font-weight: bold;
}}
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10pt auto;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    html_file = "test_rendered.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    pdf_out = "test_rendered.pdf"
    cmd = [
        CHROME_EXE,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_out}",
        html_file
    ]
    res = subprocess.run(cmd)
    print("Chrome return code:", res.returncode)
    if os.path.exists(pdf_out):
        print(f"SUCCESS! Rendered PDF. Size: {os.path.getsize(pdf_out)} bytes")
        
        # Now check if we can inspect pages
        import pypdf
        reader = pypdf.PdfReader(pdf_out)
        print("Total PDF pages:", len(reader.pages))

if __name__ == "__main__":
    test_convert()
