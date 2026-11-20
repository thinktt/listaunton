"""Build an offline comparison of rook geometries fitted at different cameras.

Each candidate retains its original physical coordinates. Rotation uses one shared
center and union bounds; selecting a candidate never normalizes its height.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import html as html_module
import json
import math
import re
import struct

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--template',type=Path,default=Path(__file__).with_name('projections-template.html'))
args=parser.parse_args()
root=args.root.resolve()
source=root/'assets/rook-projections/variants.json'
manifest=json.loads(source.read_text(encoding='utf-8'))
baseline=manifest['baseline']
rows=manifest['variants']
assert rows and baseline in [row['id'] for row in rows]
assert len({row['id'] for row in rows})==len(rows)
fields=['vertexCount','indexCount','triangleCount','vertexStrideBytes','vertexByteLength','indexByteOffset','totalByteLength','bounds','sourceSha256','referenceCamera']
public=[];buffers=[];profiles=[];renders=[];buttons=[];profile_dimensions=[]
all_bounds=[];profile_cameras=[]

def relative_file(value):
    path=(root/value).resolve()
    if root not in path.parents:raise ValueError('Asset path leaves the project root: '+str(value))
    if not path.is_file():raise FileNotFoundError(path)
    return path

def image_uri(path):
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n',f'Expected PNG: {path}'
    dimensions=struct.unpack('>II',data[16:24])
    return 'data:image/png;base64,'+base64.b64encode(data).decode('ascii'),dimensions

for row in rows:
    ident=row['id'];assert re.fullmatch(r'[a-z0-9-]+',ident),ident
    folder=row['assetDir'];meta=json.loads(relative_file(folder+'/mesh.json').read_text(encoding='utf-8'))
    binary=relative_file(folder+'/mesh.bin').read_bytes()
    blend=relative_file(row['model'])
    assert hashlib.sha256(blend.read_bytes()).hexdigest()==meta['sourceSha256'],f'Re-export {ident}: Blender model changed.'
    assert meta['referenceCamera']['type']=='ORTHO'
    validation=json.loads(relative_file(folder+'/validation.json').read_text(encoding='utf-8'))
    assert validation['sourceSha256']==meta['sourceSha256']
    for name,key in [('render.png','renderSha256'),('profile.png','profileSha256'),('camera.json','cameraSha256')]:
        assert hashlib.sha256(relative_file(folder+'/'+name).read_bytes()).hexdigest()==validation[key],f'Stale {name}: {ident}'
    assert len(binary)==meta['totalByteLength']
    assert meta['vertexStrideBytes']==24 and meta['vertexCount']*24==meta['vertexByteLength']==meta['indexByteOffset']
    assert meta['indexCount']==meta['triangleCount']*3
    assert meta['indexByteOffset']+meta['indexCount']*4==len(binary)
    all_bounds.append(meta['bounds'])
    item={key:row[key] for key in ['id','label','elevation','model']}
    item['meta']={key:meta[key] for key in fields}
    public.append(item)
    buffers.append(f'<script id="mesh-{ident}" type="application/octet-stream">'+base64.b64encode(binary).decode('ascii')+'</script>')
    profile,dimensions=image_uri(relative_file(folder+'/profile.png'));profile_dimensions.append(dimensions)
    render,render_dimensions=image_uri(relative_file(folder+'/render.png'));assert render_dimensions[0]==render_dimensions[1]
    camera_file=root/folder/'profile-camera.json'
    if camera_file.is_file():
        camera=json.loads(camera_file.read_text(encoding='utf-8'));camera=camera.get('referenceCamera',camera.get('camera',camera))
        profile_cameras.append({key:camera[key] for key in ['type','worldToCamera','projectionMatrix','width','height'] if key in camera})
    pressed=str(ident==baseline).lower();label=html_module.escape(row['label']);hidden='' if ident==baseline else ' hidden'
    profiles.append(f'<button class="profile-card" data-variant="{ident}" aria-pressed="{pressed}"><span>{label}</span><img src="{profile}" alt="Front profile of the rook geometry fitted at {row["elevation"]} degrees" draggable="false"></button>')
    renders.append(f'<img id="render-{ident}" class="render-layer" data-variant="{ident}" src="{render}" alt="Rook fitted at {row["elevation"]} degrees, rendered from its own reference camera"{hidden}>')
    buttons.append(f'<button class="variant-button" data-variant="{ident}" aria-pressed="{pressed}">{label}</button>')

assert len(set(profile_dimensions))==1,'Profile renders must share the same image dimensions.'
assert len(profile_cameras)==len(rows),'Every physical profile requires its camera evidence.'
if profile_cameras and all(profile_cameras):
    assert all(json.dumps(camera,sort_keys=True)==json.dumps(profile_cameras[0],sort_keys=True) for camera in profile_cameras),'Profile renders must use an identical camera for fair proportions.'
low=[min(b['min'][i] for b in all_bounds) for i in range(3)]
high=[max(b['max'][i] for b in all_bounds) for i in range(3)]
shared_bounds={'min':low,'max':high,'center':[(a+b)/2 for a,b in zip(low,high)],'size':[b-a for a,b in zip(low,high)]}
shared_view={'center':shared_bounds['center']}
shared_view.update(manifest.get('sharedView') or {})
assert all(math.isfinite(v) for v in shared_view['center'])
alignment=json.loads((root/'assets/rook/original-alignment.json').read_text(encoding='utf-8'))
config={'baseline':baseline,'variants':public,'sharedBounds':shared_bounds,'sharedView':shared_view,'originalAlignment':alignment}
reference,_=image_uri(root/'assets/rook/ref.png');original,_=image_uri(root/'assets/rook/original.png')
template=args.template.read_text(encoding='utf-8')
replacements={
 '__VARIANT_COUNT__':str(len(rows)),
 '__INITIAL_MODEL__':html_module.escape(next(row['model'] for row in rows if row['id']==baseline),quote=True),
 '__VARIANT_BUTTONS__':''.join(buttons),'__PROFILE_CARDS__':''.join(profiles),'__RENDER_LAYERS__':''.join(renders),
 '__REFERENCE_IMAGE__':reference,'__ORIGINAL_IMAGE__':original,
 '__PROJECTION_DATA__':json.dumps(config,separators=(',',':')).replace('</',r'<\/'),
 '__MESH_SCRIPTS__':'\n'.join(buffers),
}
for old,new in replacements.items():template=template.replace(old,new)
assert not re.search(r'__[A-Z_]+__',template),'Unfilled page template placeholder.'
out=root/'rook-projections.html';out.write_text(template,encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {len(rows)} variants. Shared center {shared_view["center"]}; no height normalization.')
