"""Compare the measured base-polish crops with the unchanged selected reference."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probe',default='build/bishop-mission/127-polish-probe')
a=p.parse_args();folder=ROOT/a.probe;record=json.loads((folder/'manifest.json').read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(ROOT/record['source'])==record['source_sha256'] and record['source_unchanged']
reference=ROOT/'assets/bishop/reference.png';ref=np.array(Image.open(reference).convert('RGBA'))
images=[('Selected white 3',ref)];metrics=[]
def erode(mask):
    mask=mask.copy()
    for _ in range(4):
        padded=np.pad(mask,1);mask=padded[1:-1,1:-1]&padded[:-2,1:-1]&padded[2:,1:-1]&padded[1:-1,:-2]&padded[1:-1,2:]
    return mask
for row in record['variants']:
    label=row['parameters']['label'];path=folder/(label+'.png');assert sha(path)==row['render_sha256']
    ar=np.array(Image.open(path).convert('RGBA'));images.append((label,ar))
    mask=erode((ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)&(ar[:,:,3]>253))
    mae=float(np.abs(ref[:,:,:3].astype(float)-ar[:,:,:3]).mean(2)[mask].mean())
    metrics.append(dict(label=label,mean_absolute_rgb_error_8bit=mae,pixels=int(mask.sum())))
for name,box,size in [('base-comparison',record['crop'],(400,256)),('glint-detail',[430,960,670,1140],(480,360))]:
    sheet=Image.new('RGB',(size[0]*len(images),size[1]+38),'#171b21');draw=ImageDraw.Draw(sheet)
    for i,(label,ar) in enumerate(images):
        im=Image.fromarray(ar).convert('RGB').crop(box).resize(size,Image.Resampling.LANCZOS)
        sheet.paste(im,(i*size[0],38));draw.text((i*size[0]+12,12),label,fill='white')
    sheet.save(folder/(name+'.png'))
result=dict(reference_sha256=sha(reference),source_model_sha256=record['source_sha256'],metrics=metrics,
    note='Cropped material diagnostics at unchanged registration; shared opaque foreground eroded four pixels. These errors are not whole-model fidelity scores. Inspect the actual glint pattern before choosing a full candidate.')
(folder/'statistics.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps(result,indent=2))
