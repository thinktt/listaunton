"""Check that available piece models are reachable and embedded from current assets."""
from pathlib import Path
import base64,hashlib,json,re,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def data(html,ident):
 match=re.search(r'<script id="'+ident+r'"[^>]*>(.*?)</script>',html,re.S)
 assert match,ident
 return match.group(1)
class LocalLinks(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key not in ('href','src') or not value:continue
   url=urlsplit(value)
   if url.scheme or url.netloc or not url.path:continue
   assert not url.path.startswith('/'),value
   assert (root/unquote(url.path)).is_file(),value
selection={'king':('Black','candidate-1'),'rook':('Black','candidate-8'),'bishop':('White','white-candidate-3'),'knight':('Black','candidate-2'),'pawn':('Black','candidate-2')}
placements=json.loads((root/'assets/candidates/alignment.json').read_text())['pieces']
for piece,(color,chosen) in selection.items():
 review=(root/f'{piece}-review.html').read_text()
 config=json.loads(data(review,'comparison-data'));page=root/f'{piece}-model.html'
 if not page.is_file():
  assert config['model'] is None,piece
  print(f'PASS: {piece} has an explicit placeholder.')
  continue
 assert config['model']['page']==page.name,piece+' model unavailable through review tab'
 html=page.read_text();LocalLinks().feed(html)
 assert 'file:///' not in html,page
 assert not re.search(r'__[A-Z][A-Z_]+__',html),page
 meta=json.loads(data(html,'mesh-metadata'));disk=json.loads((root/f'assets/{piece}/mesh.json').read_text())
 assert meta['sourceSha256']==disk['sourceSha256']==sha(root/f'models/{piece}/{piece}-rebuilt.blend'),piece+' stale model'
 assert meta['referenceCamera']==disk['referenceCamera'],piece+' stale camera'
 assert base64.b64decode(data(html,'mesh-data'))==(root/f'assets/{piece}/mesh.bin').read_bytes(),piece+' stale mesh'
 assert json.loads((root/f'assets/{piece}/camera.json').read_text())==meta['referenceCamera'],piece+' camera discrepancy'
 assert sha(root/f'assets/{piece}/original.png')==sha(root/f'references/lichess-staunton-3d/{color}-{piece.title()}.png'),piece+' changed original'
 chosen_item=next(i for i in placements[piece] if i['id']==chosen)
 reference=root/f'assets/{piece}/reference.png'
 if not reference.is_file():reference=root/f'assets/{piece}/ref.png'
 assert sha(reference)==sha(root/chosen_item['file']),piece+' wrong selected candidate'
 alignment=json.loads(data(html,'original-alignment'))
 assert alignment=={k:json.loads((root/f'assets/{piece}/original-alignment.json').read_text())[k] for k in ('scale','x','y')},piece+' stale alignment'
 print(f'PASS: {piece} review opens its current mesh/camera; selected reference and original are unchanged.')
king=json.loads(data((root/'king-review.html').read_text(),'comparison-data'))
assert king['projections']['page']=='king-projections.html'
for name in ['index.html','set-comparison.html']:
 assert 'href="king-projections.html"' in (root/name).read_text(),name
projection=(root/'king-projections.html').read_text();LocalLinks().feed(projection)
manifest=json.loads(data(projection,'projection-data'))
assert len(manifest['variants'])==5
for item in manifest['variants']:
 assert (root/item['model']).is_file(),item['id']
print('PASS: five king projection variants are linked from review, home and set comparison; local downloads exist.')
