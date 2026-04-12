#!/usr/bin/env python3
"""Post-process extracted HTML files to inline local images as base64.

The extract_inline_html.py script only embeds images with http(s) URLs.
Local image paths (e.g. src/assets/logo.png) are left as-is. This script
finds those local references and converts them to inline base64 data URIs
so the HTML file is fully self-contained.

Usage:
    python3 post_process.py <html_file> [<html_file> ...] [--base-dir <dir>]

Examples:
    # Process a single file (images resolved relative to cwd):
    python3 .agents/plugins/stitch/skills/extract-static-html/scripts/post_process.py \
        .stitch/portfolio-home.html

    # Process multiple files with a base directory for resolving image paths:
    python3 .agents/plugins/stitch/skills/extract-static-html/scripts/post_process.py \
        .stitch/home.html .stitch/about.html \
        --base-dir react-tailwindcss-portfolio
"""

import argparse
import base64
import os
import re
import sys

MIME_MAP = {
    '.svg': 'image/svg+xml',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
    '.bmp': 'image/bmp',
}

# Matches src="<local_path>" where local_path does NOT start with
# http://, https://, data:, or //  (i.e. it's a local file reference).
LOCAL_SRC_PATTERN = re.compile(
    r'src="((?!https?://|data:|//)[^"]+)"'
)


def get_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return MIME_MAP.get(ext, 'application/octet-stream')


def inline_images(html: str, base_dir: str) -> tuple[str, int]:
    """Replace local src= references with base64 data URIs.

    Returns the modified HTML and the number of images inlined.
    """
    matches = list(LOCAL_SRC_PATTERN.finditer(html))
    if not matches:
        return html, 0

    inlined = 0
    offset = 0

    for m in matches:
        local_path = m.group(1)

        # Try resolving the path: first as-is, then under base_dir
        candidates = [local_path]
        if base_dir:
            candidates.append(os.path.join(base_dir, local_path.lstrip('/')))

        resolved = None
        for candidate in candidates:
            if os.path.isfile(candidate):
                resolved = candidate
                break

        if resolved is None:
            continue

        mime = get_mime(resolved)
        with open(resolved, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()

        data_uri = f'data:{mime};base64,{b64}'
        start = m.start(1) + offset
        end = m.end(1) + offset
        html = html[:start] + data_uri + html[end:]
        offset += len(data_uri) - (end - start)
        inlined += 1

    return html, inlined


def process_file(html_path: str, base_dir: str) -> None:
    with open(html_path, 'r') as f:
        html = f.read()

    html, count = inline_images(html, base_dir)

    with open(html_path, 'w') as f:
        f.write(html)

    print(f'{html_path}: inlined {count} images ({len(html):,} bytes)')


def main():
    parser = argparse.ArgumentParser(
        description='Inline local images as base64 in extracted HTML files.'
    )
    parser.add_argument(
        'files', nargs='+',
        help='One or more HTML files to post-process.'
    )
    parser.add_argument(
        '--base-dir', default='',
        help=(
            'Base directory to prepend when resolving local image paths. '
            'Useful when the HTML references paths like "src/images/foo.jpg" '
            'but the actual file is at "<base-dir>/src/images/foo.jpg". '
            'The script tries the path as-is first, then with base-dir prepended.'
        ),
    )
    args = parser.parse_args()

    for html_path in args.files:
        if not os.path.isfile(html_path):
            print(f'WARNING: File not found, skipping: {html_path}', file=sys.stderr)
            continue
        process_file(html_path, args.base_dir)


if __name__ == '__main__':
    main()
