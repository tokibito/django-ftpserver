"""
Views for example_project.
"""

import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse


@login_required
def serve_data_file(request, path):
    """Serve files from the data directory."""
    data_dir = Path(settings.DATA_DIR)

    # Normalize the path and prevent directory traversal
    if path:
        file_path = (data_dir / path).resolve()
    else:
        file_path = data_dir

    # Security check: ensure the path is within data_dir
    try:
        file_path.relative_to(data_dir)
    except ValueError:
        raise Http404("File not found")

    if not file_path.exists():
        raise Http404("File not found")

    if file_path.is_dir():
        # Return directory listing as HTML
        return render_directory_listing(request, file_path, path)
    else:
        # Serve the file with appropriate content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = "application/octet-stream"

        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
        return response


def render_directory_listing(request, dir_path, url_path):
    """Render a simple HTML directory listing."""
    data_dir = Path(settings.DATA_DIR)

    items = []
    try:
        for item in sorted(dir_path.iterdir()):
            if item.name.startswith("."):
                continue
            relative_path = item.relative_to(data_dir)
            if item.is_dir():
                items.append(f'<li><a href="/{relative_path}/">{item.name}/</a></li>')
            else:
                items.append(f'<li><a href="/{relative_path}">{item.name}</a></li>')
    except PermissionError:
        raise Http404("Permission denied")

    # Build parent link
    parent_link = ""
    if url_path:
        parent_path = str(Path(url_path).parent)
        if parent_path == ".":
            parent_link = '<li><a href="/">..</a></li>'
        else:
            parent_link = f'<li><a href="/{parent_path}/">..</a></li>'

    current_path = f"/{url_path}" if url_path else "/"
    items_html = "\n".join(items)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Index of {current_path}</title>
    <style>
        body {{ font-family: monospace; padding: 20px; }}
        h1 {{ margin-bottom: 20px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ padding: 5px 0; }}
        a {{ text-decoration: none; color: #0066cc; }}
        a:hover {{ text-decoration: underline; }}
        .logout {{ position: absolute; top: 20px; right: 20px; }}
    </style>
</head>
<body>
    <a class="logout" href="/logout/">Logout</a>
    <h1>Index of {current_path}</h1>
    <ul>
        {parent_link}
        {items_html}
    </ul>
</body>
</html>"""

    return HttpResponse(html)
