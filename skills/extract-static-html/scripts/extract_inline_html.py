import argparse
import base64
import os
import re
import sys
import urllib.request


def is_image_url(url):
  """Skip CDN scripts, fonts, and stylesheets — only embed actual images."""
  skip = ['cdn.tailwindcss.com', 'fonts.googleapis.com', '.js', '.css']
  return not any(s in url for s in skip)


img_cache = {}


def fetch_and_encode(url):
  if url in img_cache:
    return img_cache[url]
  if not is_image_url(url):
    img_cache[url] = url
    return url
  try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
      data = resp.read()
      ct = resp.headers.get('Content-Type', 'image/jpeg')
      b64 = base64.b64encode(data).decode('ascii')
      result = f'data:{ct};base64,{b64}'
      img_cache[url] = result
      print(f'  Embedded {len(data):,} bytes <- {url[:70]}...')
      return result
  except Exception as e:
    print(f'  WARN: {e} <- {url[:70]}...')
    # Fallback to transparent 1x1 pixel GIF on failure
    fallback = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    img_cache[url] = fallback
    return fallback


def embed_images(html):
  """Replace all image URLs with base64 data URIs.

  Use single quotes for url() to avoid breaking style attributes.
  """

  # <img src="https://...">
  def replace_src(m):
    url = m.group(2)
    if url.startswith('http') and is_image_url(url):
      return f'{m.group(1)}"{fetch_and_encode(url)}"'
    return m.group(0)

  html = re.sub(r'(src=)"(https?://[^"]+)"', replace_src, html)
  # url("https://...") in styles — use SINGLE quotes to avoid breaking style="..."
  html = re.sub(
      r'url\("(https?://[^"]+)"\)',
      lambda m: f"url('{fetch_and_encode(m.group(1))}')"
      if is_image_url(m.group(1))
      else m.group(0),
      html,
  )
  # url('https://...') already single-quoted
  html = re.sub(
      r"url\('(https?://[^']+)'\)",
      lambda m: f"url('{fetch_and_encode(m.group(1))}')"
      if is_image_url(m.group(1))
      else m.group(0),
      html,
  )
  return html


def convert_styles(body):
  """Convert style={{...}} using brace-depth matching for nested values."""
  result, i = [], 0
  while i < len(body):
    sm = re.search(r'style=\{\{', body[i:])
    if not sm:
      result.append(body[i:])
      break
    result.append(body[i : i + sm.start()])
    j, depth = i + sm.end(), 2
    while j < len(body) and depth > 0:
      if body[j] == '{':
        depth += 1
      elif body[j] == '}':
        depth -= 1
      j += 1
    inner = body[i + sm.end() : j - 2]
    pairs = []
    for pm in re.finditer(r"(\w+):\s*'((?:[^'\\])*)'", inner):
      k = re.sub(r'([a-z])([A-Z])', r'\1-\2', pm.group(1)).lower()
      pairs.append(f'{k}: {pm.group(2)}')
    if not pairs:
      for pm in re.finditer(r'(\w+):\s*"((?:[^"\\])*)"', inner):
        k = re.sub(r'([a-z])([A-Z])', r'\1-\2', pm.group(1)).lower()
        pairs.append(f'{k}: {pm.group(2)}')
    result.append(
        'style="' + '; '.join(pairs) + '"'
        if pairs
        else f'style="{inner.strip()}"'
    )
    i = j
  return ''.join(result)


def fix_self_closing_tags(html):
  """Fix JSX self-closing tags that are invalid in HTML.

  In JSX, <textarea />, <div />, <span /> are valid self-closing tags.
  In HTML, only void elements (img, input, br, hr, meta, link) can self-close.
  Non-void self-closing tags like <textarea /> cause the browser to treat all
  subsequent content as children, breaking the page.
  """
  # Tags that MUST NOT be self-closed in HTML
  non_void = r'(textarea|div|span|section|button|a|p|h[1-6]|ul|ol|li|nav|main|footer|header|article|aside|form|select|option|table|tr|td|th|thead|tbody|label|fieldset|legend|details|summary|dialog|canvas|script|style|title|iframe)'
  html = re.sub(
      r'<(' + non_void + r')(\s[^>]*?)\s*/>',
      r'<\1\3></\1>',
      html,
      flags=re.IGNORECASE
  )
  return html


def fix_react_attributes(html):
  """Convert React-specific attributes to HTML equivalents."""
  html = re.sub(r'\bdefaultValue=', 'value=', html)
  html = re.sub(r'\bdefaultChecked', 'checked', html)
  html = re.sub(r'\bhtmlFor=', 'for=', html)
  return html


def convert(jsx, title, head_template, exclude_pattern=None):
  lines = jsx.split('\n')
  body_lines, in_ret = [], False
  for l in lines:
    s = l.strip()
    if (
        s.startswith('import ')
        or (s.startswith('const ') and '=>' in s)
        or s.startswith('export ')
    ):
      continue
    if 'return (' in s:
      in_ret = True
      continue
    if in_ret:
      if s == ');':
        in_ret = False
        continue
      body_lines.append(l)
  body = '\n'.join(body_lines)
  
  if exclude_pattern:
    print(f"Applying exclude pattern: {exclude_pattern}")
    body = re.sub(exclude_pattern, '', body, flags=re.DOTALL)
    
  body = re.sub(r'\bclassName=', 'class=', body)
  body = convert_styles(body)
  body = re.sub(r'<Link\s+to="[^"]*"\s+class=', '<div class=', body)
  body = re.sub(
      r'<Link\s+class="([^"]*?)"\s+to="[^"]*"', r'<div class="\1"', body
  )
  body = body.replace('</Link>', '</div>')
  body = re.sub(r'\{/\*.*?\*/\}', '', body, flags=re.DOTALL)
  for old, new in [
      ('stopColor', 'stop-color'),
      ('stopOpacity', 'stop-opacity'),
      ('strokeLinecap', 'stroke-linecap'),
      ('strokeLinejoin', 'stroke-linejoin'),
      ('strokeWidth', 'stroke-width'),
      ('strokeDasharray', 'stroke-dasharray'),
      ('strokeDashoffset', 'stroke-dashoffset'),
      ('strokeMiterlimit', 'stroke-miterlimit'),
      ('strokeOpacity', 'stroke-opacity'),
      ('fillRule', 'fill-rule'),
      ('fillOpacity', 'fill-opacity'),
      ('clipRule', 'clip-rule'),
      ('clipPath', 'clip-path'),
  ]:
    body = body.replace(f'{old}=', f'{new}=')
  # Fix JSX self-closing tags and React attributes
  body = fix_self_closing_tags(body)
  body = fix_react_attributes(body)
  body = body.strip()
  om = re.match(r'<div\s+class="([^"]*)"', body)
  if om:
    bc = om.group(1)
    body = re.sub(r'^<div\s+class="[^"]*"[^>]*>', '', body, count=1)
    if body.rstrip().endswith('</div>'):
      body = body.rstrip()[:-6]
    html = (
        head_template.replace('{{title}}', title)
        + f'<body class="{bc}">\n{body}\n</body></html>\n'
    )
  else:
    html = (
        head_template.replace('{{title}}', title)
        + f'<body>\n{body}\n</body></html>\n'
    )
  return embed_images(html)


def main():
  parser = argparse.ArgumentParser(
      description='Extract static HTML from React JSX components.'
  )
  parser.add_argument('--tailwind-config', help='Path to tailwind.config.js')
  parser.add_argument('--index-css', help='Path to index.css')
  parser.add_argument(
      '--extra-css',
      help='Path to index.html to extract custom <style> blocks and font <link> tags from'
  )
  parser.add_argument(
      '--outdir', default='.stitch', help='Output directory for HTML files (default: .stitch)'
  )
  parser.add_argument(
      '--page',
      action='append',
      help='Page to convert in format: src_file:dst_filename:title',
  )
  parser.add_argument(
      '--exclude-pattern',
      help='Regex pattern to exclude from the body HTML (e.g., for dialogs)',
  )

  args = parser.parse_args()

  if not args.page:
    print('Error: No pages specified. Use --page src_file:dst_filename:title')
    sys.exit(1)

  # Build HEAD template
  tailwind_js = ''
  if args.tailwind_config and os.path.exists(args.tailwind_config):
    with open(args.tailwind_config) as f:
      content = f.read()
      # Replace export default / module.exports with tailwind.config =
      tailwind_js = re.sub(
          r'export\s+default\s+', 'tailwind.config = ', content
      )
      tailwind_js = re.sub(
          r'module\.exports\s*=\s*', 'tailwind.config = ', tailwind_js
      )
      # Remove Node-style requires that fail in the browser
      tailwind_js = re.sub(
          r'.*require\([\'"]tailwindcss/colors[\'"]\).*?\n?', '', tailwind_js
      )

  css_content = ''
  imports = []
  if args.index_css and os.path.exists(args.index_css):
    with open(args.index_css) as f:
      for line in f:
        if line.strip().startswith('@import'):
          imports.append(line.strip())
        elif not line.strip().startswith('@tailwind'):
          css_content += line

  # Extract custom CSS from index.html (custom gradients, scrollbar styles, etc.)
  extra_css = ''
  extra_links = []
  if args.extra_css and os.path.exists(args.extra_css):
    with open(args.extra_css) as f:
      html_content = f.read()
    # Extract all <style>...</style> blocks
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL):
      extra_css += m.group(1).strip() + '\n'
    # Extract Google Fonts and other stylesheet <link> tags (skip index.css)
    for m in re.finditer(r'<link[^>]+href="([^"]+)"[^>]*rel="stylesheet"[^>]*/?>|<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"[^>]*/?>',  html_content):
      href = m.group(1) or m.group(2)
      if href and href.startswith('http'):
        extra_links.append(href)

  head_template = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{{title}}</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
"""
  for imp in imports:
    # Convert @import url('...') to <link rel="stylesheet" href="..."/>
    m = re.search(r"url\(['\"]([^'\"]+)['\"]\)", imp)
    if m:
      head_template += f'<link href="{m.group(1)}" rel="stylesheet"/>\n'

  # Inject extra font links from index.html
  for href in extra_links:
    head_template += f'<link href="{href}" rel="stylesheet"/>\n'

  if tailwind_js:
    head_template += f'<script>\n{tailwind_js}\n</script>\n'

  # Combine all CSS: base styles + index.css + extra CSS from index.html
  all_css = f'body {{\n  min-height: 100dvh;\n}}\n{css_content}\n{extra_css}'
  head_template += (
      f'<style>\n{all_css}</style>\n</head>\n'
  )

  os.makedirs(args.outdir, exist_ok=True)

  for page_spec in args.page:
    parts = page_spec.split(':')
    if len(parts) != 3:
      print(
          f"Error: Invalid page spec '{page_spec}'. Must be"
          ' src_file:dst_filename:title'
      )
      continue
    src, dst_name, title = parts
    dst = os.path.join(args.outdir, dst_name)

    if not os.path.exists(src):
      print(f'Error: Source file not found: {src}')
      continue

    print(f"\n{'='*60}")
    print(f'Converting {src} -> {dst_name}...')
    print(f"{'='*60}")

    with open(src) as f:
      jsx = f.read()

    html = convert(jsx, title, head_template, exclude_pattern=args.exclude_pattern)

    with open(dst, 'w') as f:
      f.write(html)

    print(f'=> {dst} ({os.path.getsize(dst):,} bytes)')

  print(f'\nDONE: {len(img_cache)} unique images embedded.')


if __name__ == '__main__':
  main()
