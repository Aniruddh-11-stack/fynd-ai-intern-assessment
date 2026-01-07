import markdown
import os

try:
    with open('REPORT.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert to HTML with tables extension
    html_body = markdown.markdown(text, extensions=['tables'])

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fynd AI Assessment Report</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown-light.min.css">
    <style>
        body {{
            box-sizing: border-box;
            min-width: 200px;
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
        }}
        @media print {{
            body {{
                padding: 0;
                max-width: 100%;
            }}
            .markdown-body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body class="markdown-body">
{html_body}
</body>
</html>
"""

    with open('REPORT.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Success: REPORT.html created.")
except Exception as e:
    print(f"Error: {e}")
