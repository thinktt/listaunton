"""Check that available piece models are reachable and embedded from current assets."""
from pathlib import Path
import base64,hashlib,json,math,re,struct,sys
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
placements=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))['pieces']
for piece,(color,chosen) in selection.items():
 review=(root/f'{piece}-review.html').read_text(encoding='utf-8')
 config=json.loads(data(review,'comparison-data'));page=root/f'{piece}-model.html'
 if not page.is_file():
  assert config['model'] is None,piece
  print(f'PASS: {piece} has an explicit placeholder.')
  continue
 assert config['model']['page']==page.name,piece+' model unavailable through review tab'
 html=page.read_text(encoding='utf-8');LocalLinks().feed(html)
 assert 'file:///' not in html,page
 assert not re.search(r'__[A-Z][A-Z_]+__',html),page
 meta=json.loads(data(html,'mesh-metadata'));disk=json.loads((root/f'assets/{piece}/mesh.json').read_text(encoding='utf-8'))
 assert meta['sourceSha256']==disk['sourceSha256']==sha(root/f'models/{piece}/{piece}-rebuilt.blend'),piece+' stale model'
 assert meta['referenceCamera']==disk['referenceCamera'],piece+' stale camera'
 assert base64.b64decode(data(html,'mesh-data'))==(root/f'assets/{piece}/mesh.bin').read_bytes(),piece+' stale mesh'
 assert json.loads((root/f'assets/{piece}/camera.json').read_text(encoding='utf-8'))==meta['referenceCamera'],piece+' camera discrepancy'
 assert sha(root/f'assets/{piece}/original.png')==sha(root/f'references/lichess-staunton-3d/{color}-{piece.title()}.png'),piece+' changed original'
 chosen_item=next(i for i in placements[piece] if i['id']==chosen)
 reference=root/f'assets/{piece}/reference.png'
 if not reference.is_file():reference=root/f'assets/{piece}/ref.png'
 assert sha(reference)==sha(root/chosen_item['file']),piece+' wrong selected candidate'
 alignment=json.loads(data(html,'original-alignment'))
 assert alignment=={k:json.loads((root/f'assets/{piece}/original-alignment.json').read_text(encoding='utf-8'))[k] for k in ('scale','x','y')},piece+' stale alignment'
 original_item=next(i for i in placements[piece] if i['id']==color.lower())
 expected_alignment={'scale':chosen_item['scale']/original_item['scale'],'x':(chosen_item['x']-original_item['x'])/original_item['scale'],'y':(chosen_item['y']-original_item['y'])/original_item['scale']}
 for key in ('scale','x','y'):assert abs(alignment[key]-expected_alignment[key])<1e-9,piece+' wrong original registration'
 for ident,path in [('original-image',root/f'assets/{piece}/original.png'),('reference-image',reference),('model-image',root/f'assets/{piece}/render.png')]:
  encoded=re.search(r'<img id="'+ident+r'"[^>]*src="data:image/png;base64,([^"]+)"',html)
  assert encoded,piece+' missing embedded '+ident
  assert base64.b64decode(encoded.group(1))==path.read_bytes(),piece+' stale embedded '+ident
 print(f'PASS: {piece} review opens its current mesh/camera/render; source images and registration are correct.')

class PageFacts(LocalLinks):
 def __init__(self):
  super().__init__();self.elements={};self.profiles={};self.buttons=[];self.hrefs=set();self.profile=None
 def handle_starttag(self,tag,attrs):
  super().handle_starttag(tag,attrs);attrs=dict(attrs)
  if 'id' in attrs:self.elements[attrs['id']]=(tag,attrs)
  if tag=='a' and 'href' in attrs:self.hrefs.add(attrs['href'])
  if tag=='button':
   self.buttons.append(attrs)
   if 'profile-card' in attrs.get('class','').split():self.profile=attrs.get('data-variant')
  if tag=='img' and self.profile:self.profiles[self.profile]=attrs
 def handle_endtag(self,tag):
  if tag=='button':self.profile=None

def facts(html):
 page=PageFacts();page.feed(html);return page

def project_file(relative):
 path=(root/relative).resolve()
 assert root in path.parents and path.is_file(),'Missing or non-project file: '+str(relative)
 return path

def read_json(path):return json.loads(path.read_text(encoding='utf-8'))

def camera(value):return value.get('referenceCamera',value.get('camera',value))

def embedded_png(attrs,path,label):
 value=attrs.get('src','');prefix='data:image/png;base64,'
 assert value.startswith(prefix),label+' must embed a PNG'
 raw=base64.b64decode(value[len(prefix):],validate=True)
 assert raw==path.read_bytes(),label+' is stale'
 assert raw[:8]==b'\x89PNG\r\n\x1a\n',label+' is not PNG'
 return struct.unpack('>II',raw[16:24])

expected_angles={'king':[48,52,54,56,60,64],'rook':[48,52,54,56,60,64],'queen':[48,51.5,52,54,56,60,64]}
homepage_links={name:facts((root/name).read_text(encoding='utf-8')).hrefs for name in ['index.html','set-comparison.html']}
for piece,angles in expected_angles.items():
 page_path=root/f'{piece}-projections.html';source_path=root/f'assets/{piece}-projections/variants.json'
 if not page_path.is_file() and not source_path.is_file():
  print(f'SKIP: {piece} projection study is not installed.');continue
 assert page_path.is_file() and source_path.is_file(),piece+' projection study is only partially installed'
 for name,links in homepage_links.items():assert page_path.name in links,piece+' projection link missing from '+name
 review_path=root/('review.html' if piece=='queen' else f'{piece}-review.html')
 review=review_path.read_text(encoding='utf-8');review_facts=facts(review)
 if piece=='queen':
  tabs=[b for b in review_facts.buttons if b.get('data-workspace')=='projections']
  assert len(tabs)==1 and tabs[0].get('aria-controls')=='projections-pane','Queen projection workspace tab is missing'
  _,pane=review_facts.elements['projections-pane'];tag,frame=review_facts.elements['projections-frame']
  assert 'hidden' in pane and tag=='iframe' and not frame.get('src'),'Queen projection iframe must start unloaded'
  assert {'allow-scripts','allow-downloads'}<=set(frame.get('sandbox','').split()),'Queen projection frame sandbox missing required capabilities'
  runtime=data(review,'review-runtime')
  assert 'projectionsStarted' in runtime and re.search(r"\.src\s*=\s*['\"]queen-projections\.html['\"]",runtime),'Queen lazy projection target is missing'
 else:
  config=json.loads(data(review,'comparison-data'))
  assert config.get('projections',{}).get('page')==page_path.name,piece+' projection study unavailable through review tab'
  tabs=[b for b in review_facts.buttons if b.get('id')=='tab-projections']
  assert len(tabs)==1 and tabs[0].get('aria-controls')=='panel-projections',piece+' projection tab is missing'
  tag,frame=review_facts.elements['projections-frame']
  assert tag=='iframe' and not frame.get('src'),piece+' projection frame must start unloaded'
  assert {'allow-scripts','allow-downloads'}<=set(frame.get('sandbox','').split()),piece+' projection sandbox missing required capabilities'
 html=page_path.read_text(encoding='utf-8');page=facts(html)
 assert 'file:///' not in html and not re.search(r'__[A-Z][A-Z_]+__',html),piece+' unresolved projection page'
 source=read_json(source_path);embedded=json.loads(data(html,'projection-data'))
 rows=source['variants'];shown=embedded['variants'];ids=[row['id'] for row in rows]
 assert len(ids)==len(set(ids)) and [row['id'] for row in shown]==ids,piece+' projection variants disagree with assets'
 assert sorted(row['elevation'] for row in rows)==angles and 54 in angles,piece+' unexpected projection angles'
 assert embedded['baseline']==source['baseline'] and source['baseline'] in ids,piece+' wrong baseline'
 bounds=[];profile_cameras=[];profile_dimensions=[];base_widths=[]
 for row,item in zip(rows,shown):
  label=piece+' '+row['id'];folder=row['assetDir']
  assert {key:item[key] for key in ['id','label','elevation','model']}=={key:row[key] for key in ['id','label','elevation','model']},label+' stale manifest item'
  model=project_file(row['model']);meta=read_json(project_file(folder+'/mesh.json'));binary=project_file(folder+'/mesh.bin').read_bytes()
  fields=['vertexCount','indexCount','triangleCount','vertexStrideBytes','vertexByteLength','indexByteOffset','totalByteLength','bounds','sourceSha256','referenceCamera']
  assert item['meta']=={key:meta[key] for key in fields},label+' stale embedded mesh metadata'
  assert item['meta']['sourceSha256']==meta['sourceSha256']==sha(model),label+' model and mesh disagree'
  assert base64.b64decode(data(html,'mesh-'+row['id']),validate=True)==binary,label+' stale embedded mesh'
  assert len(binary)==meta['totalByteLength'] and meta['vertexStrideBytes']==24,label+' invalid mesh size/stride'
  assert meta['vertexCount']*24==meta['vertexByteLength']==meta['indexByteOffset'],label+' invalid vertex layout'
  assert meta['indexCount']==meta['triangleCount']*3 and meta['indexByteOffset']+meta['indexCount']*4==len(binary),label+' invalid index layout'
  own_camera=camera(read_json(project_file(folder+'/camera.json')))
  assert own_camera==meta['referenceCamera']==item['meta']['referenceCamera'] and own_camera['type']=='ORTHO',label+' stale saved reference camera'
  _,render=page.elements['render-'+row['id']]
  assert render.get('data-variant')==row['id'],label+' render selects wrong model'
  dimensions=embedded_png(render,project_file(folder+'/render.png'),label+' render')
  assert dimensions==(own_camera['width'],own_camera['height']),label+' render/camera dimensions differ'
  profile_dimensions.append(embedded_png(page.profiles[row['id']],project_file(folder+'/profile.png'),label+' profile'))
  profile_camera=camera(read_json(project_file(folder+'/profile-camera.json')))
  profile_cameras.append({key:profile_camera[key] for key in ['type','worldToCamera','projectionMatrix','width','height']})
  assert profile_dimensions[-1]==(profile_camera['width'],profile_camera['height']),label+' profile/camera dimensions differ'
  evidence_path=root/folder/'validation.json'
  if evidence_path.is_file():
   evidence=read_json(evidence_path)
   if 'sourceSha256' in evidence:assert evidence['sourceSha256']==meta['sourceSha256'],label+' stale validation model'
   for filename,key in [('render.png','renderSha256'),('profile.png','profileSha256'),('camera.json','cameraSha256')]:
    if key in evidence:assert evidence[key]==sha(project_file(folder+'/'+filename)),label+' stale '+filename+' evidence'
  bounds.append(meta['bounds'])
  if 'baseWidth' in row:base_widths.append(row['baseWidth'])
 assert len(set(profile_dimensions))==1 and all(c==profile_cameras[0] for c in profile_cameras),piece+' physical profiles do not share one camera and scale'
 if base_widths:assert len(base_widths)==len(rows) and max(base_widths)-min(base_widths)<max(base_widths)*1e-5,piece+' projection base widths differ'
 low=[min(b['min'][i] for b in bounds) for i in range(3)];high=[max(b['max'][i] for b in bounds) for i in range(3)]
 shared={'min':low,'max':high,'center':[(a+b)/2 for a,b in zip(low,high)],'size':[b-a for a,b in zip(low,high)]}
 assert embedded['sharedBounds']==shared,piece+' stale union bounds'
 shared_view={'center':shared['center']};shared_view.update(source.get('sharedView') or {})
 assert embedded['sharedView']==shared_view and all(math.isfinite(v) for v in shared_view['center']),piece+' incorrect shared rotation center/scale'
 baseline=next(row for row in rows if row['id']==source['baseline'])
 assert page.elements['model-download'][1].get('href')==baseline['model'],piece+' initial download is not its baseline model'
 original=root/(f'assets/{piece}-projections/original.png' if piece=='queen' else f'assets/{piece}/original.png')
 reference=root/(f'assets/{piece}-projections/reference.png' if piece=='queen' else f'assets/{piece}/reference.png')
 if not reference.is_file():reference=root/f'assets/{piece}/ref.png'
 embedded_png(page.elements['original-image'][1],original,piece+' original reference')
 embedded_png(page.elements['reference-image'][1],reference,piece+' selected reference')
 print(f'PASS: {len(rows)} {piece} projections are linked from review/home/set; downloads, embedded meshes/renders/cameras and shared physical profile scale match their assets.')
