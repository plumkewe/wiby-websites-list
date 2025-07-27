import os
import csv

def create_modern_html_page_same_folder(
    input_csv='websites.csv',
    images_dir='screenshot_thumbnails',
    output_html='index.html'
):
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Aggiunge index se mancante e ordina
    if "index" in fieldnames:
        rows.sort(key=lambda x: int(x.get('index', 0)))
    else:
        for i, row in enumerate(rows):
            row["index"] = str(i + 1)
        fieldnames = ["index"] + fieldnames

    # Inserisce screenshot, title, description dopo index
    filtered = [c for c in fieldnames if c not in ('title', 'description')]
    new_fields = []
    for c in filtered:
        new_fields.append(c)
        if c == 'index':
            new_fields += ['screenshot', 'title', 'description']

    # Inizio HTML
    html = [
        '<!DOCTYPE html>',
        '<html lang="en"><head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Wiby list</title>',
        '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">',
        '  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css">',
        '  <style>',
        '    .screenshot-cell {',
        '      width: 238px;',
        '      height: 109px;',
        '      text-align: center;',
        '      vertical-align: middle;',
        '    }',
        '    img.thumbnail {',
        '      width: 221px;',
        '      height: auto;',
        '      object-fit: cover;',
        '    }',
        '    .desc-clamp {',
        '      width: 400px;',
        '      max-height: 92px;',
        '      overflow: scroll;',
        '      position: relative;',
        '    }',
        '    .read-more {',
        '      cursor: pointer;',
        '      color: #0d6efd;',
        '      text-decoration: underline;',
        '      display: none;',
        '      margin-top: 5px;',
        '    }',
        '    .expanded { max-height: none !important; }',
        '    th, td { vertical-align: middle; }',
        '    td.title-cell {',
        '      width: 300px;',
        '      min-width: 300px;',
        '      max-width: 300px;',
        '      word-wrap: break-word;',
        '      white-space: normal;',
        '    }',
        '    .table-responsive {',
        '      overflow-x: auto;',
        '      -ms-overflow-style: none;',
        '      scrollbar-width: none;',
        '    }',
        '    .table-responsive::-webkit-scrollbar { display: none; }',
        '  </style>',
        '</head><body>',
        '<div class="container py-4">',
        '  <h1 class="mb-4">Wiby list</h1>',
        '  <div class="table-responsive">',
        '    <table id="websites-table" class="table table-bordered table-hover table-striped align-middle">',
        '      <thead><tr>'
    ]

    for c in new_fields:
        html.append(f'        <th>{c.capitalize()}</th>')
    html.append('      </tr></thead><tbody>')

    for row in rows:
        html.append('      <tr>')
        for c in new_fields:
            value = row.get(c, '')
            if c == 'screenshot':
                idx = row.get('index', '')
                fn = f"{idx}.png"
                url = row.get('url', '#').replace('"', '&quot;')
                img_path = os.path.join(images_dir, fn)
                html.append('<td class="screenshot-cell">')
                if os.path.exists(img_path):
                    html.append(
                        f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                        f'<img src="{images_dir}/{fn}" class="thumbnail" alt="screenshot"></a>'
                    )
                html.append('</td>')
            elif c == 'url':
                html.append(f'<td class="url-cell"><a href="{value}" target="_blank" rel="noopener noreferrer">{value}</a></td>')
            elif c == 'title':
                escaped_value = value.replace('"', '&quot;')
                html.append(f'<td class="title-cell">{escaped_value}</td>')
            elif c == 'description':
                escaped_value = value.replace('"', '&quot;')
                html.append(
                    '<td>'
                    f'<div class="desc-clamp">{escaped_value}</div>'
                    f'<span class="read-more">Read more</span>'
                    '</td>'
                )
            elif c == 'creation_date':
                html.append(f'<td class="data-cell">{value}</td>')
            elif c == 'domain':
                html.append(f'<td class="domain-cell">{value}</td>')
            else:
                html.append(f'<td>{value}</td>')
        html.append('      </tr>')

    order_column = new_fields.index("index") if "index" in new_fields else 0

    html += [
        '  </tbody></table>',
        '  </div>',
        '</div>',
        '<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>',
        '<script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>',
        '<script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>',
        '<script>',
        '  $(function() {',
        f'    var table = $("#websites-table").DataTable({{"order": [[{order_column}, "asc"]],',
        '      "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]',
        '    });',
        '    $(".desc-clamp").each(function() {',
        '      if (this.scrollHeight > 92) {',
        '        $(this).next(".read-more").show();',
        '      }',
        '    });',
        '    $(".read-more").on("click", function() {',
        '      var desc = $(this).prev(".desc-clamp");',
        '      desc.toggleClass("expanded");',
        '      $(this).text(desc.hasClass("expanded") ? "Show less" : "Read more");',
        '    });',
        '  });',
        '</script>',
        '</body></html>'
    ]

    out = os.path.join(os.path.dirname(__file__), output_html)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
        
    print(f"Generated: {out}")

if __name__ == "__main__":
    create_modern_html_page_same_folder()