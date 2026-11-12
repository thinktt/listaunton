"""Inspect actual fixed-frame base-light probes without moving reference pixels."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--probe', required=True)
a = p.parse_args()
folder = ROOT/a.probe
manifest = json.loads((folder/'manifest.json').read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(ROOT/manifest['source']) == manifest['source_sha256']
reference = ROOT/'assets/bishop/reference.png'
ref = np.array(Image.open(reference).convert('RGBA'))
images = [('Selected white 3', ref)]
rows = []
regions = {'base and foot':[240,825,780,1170], 'glint':[525,950,655,1040],
           'foot':[240,1040,780,1130]}

def erode(mask):
    for _ in range(4):
        q = np.pad(mask, 1)
        mask = q[1:-1,1:-1]&q[:-2,1:-1]&q[2:,1:-1]&q[1:-1,:-2]&q[1:-1,2:]
    return mask

for record in manifest['variants']:
    label = record['parameters']['label']
    path = folder/(label+'.png')
    assert sha(path) == record['render_sha256']
    ar = np.array(Image.open(path).convert('RGBA'))
    images.append((label, ar))
    mask = erode((ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)&(ar[:,:,3]>253))
    error = np.abs(ref[:,:,:3].astype(float)-ar[:,:,:3]).mean(2)
    result = {}
    for name, (x0,y0,x1,y1) in regions.items():
        m = mask[y0:y1,x0:x1]
        result[name] = dict(pixels=int(m.sum()), mean_absolute_rgb_error_8bit=float(error[y0:y1,x0:x1][m].mean()))
    rows.append(dict(label=label, regions=result))

for name, box, size in [('base-comparison',regions['base and foot'],(360,230)),
                        ('glint-detail',[490,930,690,1070],(400,280))]:
    columns = min(4, len(images))
    sheets = (len(images)+columns-1)//columns
    sheet = Image.new('RGB',(columns*size[0],sheets*(size[1]+34)),'#171b21')
    draw = ImageDraw.Draw(sheet)
    for i,(label,ar) in enumerate(images):
        x,y = (i%columns)*size[0],(i//columns)*(size[1]+34)
        im = Image.fromarray(ar).convert('RGB').crop(box).resize(size,Image.Resampling.LANCZOS)
        sheet.paste(im,(x,y+34))
        draw.text((x+10,y+10),label,fill='white')
    sheet.save(folder/(name+'.png'))

result = dict(reference_sha256=sha(reference), source_model_sha256=manifest['source_sha256'],
              metrics=rows, note='Actual BSDF crop errors at fixed registration. Shared opaque foreground eroded four pixels. Provisional powers are not optimized. These are not full-model fidelity percentages.')
(folder/'statistics.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps(result,indent=2))
