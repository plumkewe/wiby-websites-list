import csv
import os
import json

def color_dot(rgb_str):
    try:
        rgb = tuple(map(int, rgb_str.strip("() ").split(",")))
        if len(rgb) != 3:
            raise ValueError
        return f'<span class="color-dot" style="background-color: rgb{rgb};"></span>{rgb_str}'
    except:
        return '<span class="text-muted">N/A</span>'

def generate_row(data, screenshot_folder):
    idx = data['index']
    img_html = '<div class="text-muted">No image</div>'
    for ext in ['png', 'jpg', 'jpeg']:
        path = os.path.join(screenshot_folder, f"{idx}.{ext}")
        if os.path.exists(path):
            img_html = f'<img src="{path}" class="screenshot" onclick="window.open(\'{data["url"]}\')">'
            break
    return [
        idx,
        img_html,
        f'<div class="scrollable-text">{data["title"]}</div>',
        f'<div class="scrollable-text">{data["description"]}</div>',
        f'<a href="{data["url"]}" target="_blank">{data["url"]}</a>',
        data['creation_date'],
        data['domain'],
        color_dot(data['primary']),
        color_dot(data['secondary']),
        color_dot(data['tertiary']),
    ]

def main():
    data_rows = []
    with open('websites.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            data_rows.append(generate_row(row, 'screenshot_thumbnails'))

    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="theme-color" content="#ffffff">
    <title>Wiby list</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
    <style>
        html, body {{
            background-color: #ffffff;
        }}
        .scrollable-text {{
            max-height: 109px;
            overflow-y: auto;
            white-space: normal;
            text-overflow: unset;
        }}
        .screenshot {{
            width: 221px;
            height: auto;
            cursor: pointer;
        }}
        .color-dot {{
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
        }}
        table {{
            table-layout: fixed;
            width: 100%;
        }}
        table td {{
            vertical-align: middle;
            height: 109px;
            max-height: 109px;
            overflow: hidden;
        }}
        td .scrollable-text {{
            white-space: normal;
            text-overflow: unset;
        }}
        table th {{
            text-transform: uppercase;
            font-weight: bold;
            vertical-align: middle;
        }}
        /* Blur overlay styles */
        #loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        body.loading #page-content {{
            filter: blur(4px);
            pointer-events: none;
        }}
    </style>
</head>
<body class="loading">

    <!-- Loading Overlay -->
    <div id="loading-overlay">
        <div class="spinner-border text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="container-fluid" id="page-content">
        <h2>Wiby list</h2>
        <table id="webTable" class="table table-striped">
            <thead class="table-dark">
                <tr>
                    <th>INDEX</th>
                    <th>SCREENSHOT</th>
                    <th>TITLE</th>
                    <th>DESCRIPTION</th>
                    <th>URL</th>
                    <th>CREATION_DATE</th>
                    <th>DOMAIN</th>
                    <th>PRIMARY</th>
                    <th>SECONDARY</th>
                    <th>TERTIARY</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
    <script>
        const data = {json.dumps(data_rows)};

        $(document).ready(function () {{
            $('body').addClass('loading');

            $('#webTable').DataTable({{
                data: data,
                pageLength: 10,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                columns: [
                    {{ title: "INDEX", width: "84px" }},
                    {{ title: "SCREENSHOT", width: "236px" }},
                    {{ title: "TITLE", width: "220px" }},
                    {{ title: "DESCRIPTION", width: "300px" }},
                    {{ title: "URL", width: "220px" }},
                    {{ title: "CREATION_DATE", width: "168px" }},
                    {{ title: "DOMAIN", width: "216px" }},
                    {{ title: "PRIMARY", width: "216px" }},
                    {{ title: "SECONDARY", width: "216px" }},
                    {{ title: "TERTIARY", width: "216px" }}
                ],
                initComplete: function () {{
                    $('#loading-overlay').fadeOut(300);
                    $('body').removeClass('loading');
                }}
            }});
        }});
    </script>
</body>
</html>
'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html generato con blur e animazione di caricamento.")

if __name__ == "__main__":
    main()
    