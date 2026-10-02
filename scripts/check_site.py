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
for name in ('index.html', 'review.html'):
    html = (ROOT / name).read_text(encoding='utf-8')
    assert 'file:///' not in html, f'Machine-specific URL in {name}'
    Links().feed(html)
review = (ROOT / 'review.html').read_text(encoding='utf-8')
initial_style = re.search(r'<style>(.*?)</style>', review, re.S).group(1)
assert '#stage #contours{z-index:3;display:none}' in initial_style, 'Contour hiding must beat the #stage img selector before JS starts'
assert '#stage{visibility:hidden;' in initial_style, 'Keep the image hidden until the initial fit is ready'
assert '#render{z-index:2;opacity:.5}' in initial_style
assert 'cursor:grab' not in initial_style, 'Reference view should use the normal cursor'

for value in re.findall(r"['\"](assets/queen/[^'\"]+\.png)['\"]", review):
    assert (ROOT / value).is_file(), value
def embedded(identifier):
    return json.loads(re.search(r'<script id="'+identifier+r'"[^>]*>(.*?)</script>', review, re.S).group(1))
parts = embedded('parts-document')
assert parts == (ROOT/'scripts/queen/parts-template.html').read_text(encoding='utf-8')
assert 'id="details-section"' not in review
for obsolete in ('queen-3d.html', 'queen-parts.html', 'staunton-references.html'):
    assert not (ROOT/obsolete).exists(), obsolete
assert 'sandbox="allow-scripts"' in parts
assert 'Content-Security-Policy' in parts
viewer = embedded('viewer-document')
Links().feed(viewer)
meta = re.search(r'<script id="mesh-metadata"[^>]*>(.*?)</script>', viewer, re.S)
assert meta, 'Missing viewer mesh metadata'
expected = json.loads(meta.group(1))['sourceSha256']
actual = hashlib.sha256((ROOT / 'models/queen/queen-rebuilt.blend').read_bytes()).hexdigest()
assert expected == actual, 'Viewer is stale relative to the Blender model'
print(f'PASS: two pages, {len(checked)} local links, overlay images, parts sandbox/CSP, and model/viewer hash.')

manifest=json.loads((ROOT/'references/lichess-staunton-3d/original-png-manifest.json').read_text())
assert len(manifest['files'])==12
gallery=(ROOT/'index.html').read_text(encoding='utf-8')
assert gallery.count('data-piece=')==5
assert 'href="review.html"' in gallery
assert gallery.count('<img ')==12
for item in manifest['files']:
    image=ROOT/'references/lichess-staunton-3d'/item['file']
    assert hashlib.sha256(image.read_bytes()).hexdigest()==item['sha256'],item['file']
    assert f'src="references/lichess-staunton-3d/{item["file"]}"' in gallery
print('PASS: all twelve original PNG reference hashes and gallery images.')

alignment=json.loads(re.search(r'<script id="original-reference-alignment"[^>]*>(.*?)</script>',review,re.S).group(1))
assert alignment==json.loads((ROOT/'assets/queen/original-reference-alignment.json').read_text())
for label in ('source','target'):
    assert hashlib.sha256((ROOT/alignment[label]).read_bytes()).hexdigest()==alignment[label+'_sha256']
print('PASS: original-reference alignment metadata and source image hashes.')
