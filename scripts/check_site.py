"""Check local links, dynamic overlay images, sandbox and mesh provenance."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
checked = set()
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            assert not url.path.startswith('/'), f'Nonportable root link: {value}'
            target = ROOT / unquote(url.path)
            assert target.is_file(), f'Missing local link: {value}'
            checked.add(url.path)
for name in ('index.html', 'queen-3d.html', 'review.html', 'queen-parts.html'):
    html = (ROOT / name).read_text(encoding='utf-8')
    assert 'file:///' not in html, f'Machine-specific URL in {name}'
    Links().feed(html)
review = (ROOT / 'review.html').read_text(encoding='utf-8')
for value in re.findall(r"['\"](assets/queen/[^'\"]+\.png)['\"]", review):
    assert (ROOT / value).is_file(), value
parts = (ROOT / 'queen-parts.html').read_text(encoding='utf-8')
assert 'sandbox="allow-scripts"' in parts
assert 'Content-Security-Policy' in parts
viewer = (ROOT / 'queen-3d.html').read_text(encoding='utf-8')
meta = re.search(r'<script id="mesh-metadata"[^>]*>(.*?)</script>', viewer, re.S)
assert meta, 'Missing viewer mesh metadata'
expected = json.loads(meta.group(1))['sourceSha256']
actual = hashlib.sha256((ROOT / 'models/queen/queen-rebuilt.blend').read_bytes()).hexdigest()
assert expected == actual, 'Viewer is stale relative to the Blender model'
print(f'PASS: four pages, {len(checked)} local links, overlay images, parts sandbox/CSP, and model/viewer hash.')
