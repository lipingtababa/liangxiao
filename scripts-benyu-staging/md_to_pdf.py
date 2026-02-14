#!/usr/bin/env python3
"""Convert markdown file to PDF with Chinese font support."""

import sys
import markdown
from weasyprint import HTML

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        h1 {{ font-size: 18pt; margin-top: 24pt; }}
        h2 {{ font-size: 14pt; margin-top: 18pt; color: #333; }}
        h3 {{ font-size: 12pt; margin-top: 14pt; color: #555; }}
        p {{ margin: 8pt 0; text-align: justify; }}
        strong {{ color: #000; }}
        ol, ul {{ margin: 8pt 0; padding-left: 24pt; }}
        li {{ margin: 4pt 0; }}
        a {{ color: #0066cc; }}
        hr {{ border: none; border-top: 1px solid #ccc; margin: 16pt 0; }}
    </style>
</head>
<body>
{content}
</body>
</html>
'''

def convert(md_path: str, pdf_path: str = None):
    """Convert markdown file to PDF."""
    if pdf_path is None:
        pdf_path = md_path.rsplit('.', 1)[0] + '.pdf'

    with open(md_path, 'r') as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=['extra'])
    full_html = HTML_TEMPLATE.format(content=html_content)

    HTML(string=full_html).write_pdf(pdf_path)
    print(f'PDF created: {pdf_path}')
    return pdf_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 md_to_pdf.py <markdown_file> [output_pdf]')
        sys.exit(1)

    md_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert(md_path, pdf_path)
