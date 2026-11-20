"""Show fixed-coordinate collar crops and diagnostic RGB differences."""
import argparse,json,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',default='build/bishop-mission/107-collar-isolation');p.add_argument('--partial',action='store_true')
a=p.parse_args();folder=ROOT/a.folder;box=(290,405,690,630);ref=Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA');w=ref.width
def original(name,alignment):
    q=json.loads((ROOT/'assets/bishop'/alignment).read_text());s=q['scale']*300/w
    return Image.open(ROOT/'assets/bishop'/name).convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(s,0,q['x']*3,0,s,q['y']*3),Image.Resampling.BILINEAR)
images=[('Original white (enlarged)',original('original.png','original-alignment.json')),
 ('Original black (enlarged)',original('black-original.png','black-alignment.json')),('Selected white 3',ref)]
labels=['control','without-collar','without-head','without-both','without-relief','double-collar']
for label in labels:
    path=folder/(label+'.png')
    if path.exists():images.append((label,Image.open(path).convert('RGBA')))
    else:assert a.partial,path
cols=3;cw,ch=600,375;rows=(len(images)+cols-1)//cols;canvas=Image.new('RGB',(cols*cw,rows*ch),'#171b21');draw=ImageDraw.Draw(canvas)
scores={};reference=np.array(ref.crop(box),dtype=np.float32)
for i,(label,im) in enumerate(images):
    x,y=(i%cols)*cw,(i//cols)*ch;crop=im.crop(box)
    resized=crop.resize((600,338),Image.Resampling.LANCZOS);canvas.paste(resized,(x,y+32),resized)
    draw.text((x+12,y+10),label,fill='white')
    if label in labels:
        ar=np.array(crop,dtype=np.float32);mask=(reference[:,:,3]>127)&(reference[:,:,:3].max(2)>12)&(ar[:,:,3]>254)
        mask=blur(mask.astype(np.float32),3)>.999
        core=mask&(reference[:,:,0]>210)&(reference[:,:,1]>150)&(reference[:,:,2]>70)
        scores[label]={'shared_pixels':int(mask.sum()),'mean_absolute_rgb_error_8bit':float(np.abs(ar[:,:,:3][mask]-reference[:,:,:3][mask]).mean()),
          'reference_core_pixels':int(core.sum()),'reference_core_mae_8bit':float(np.abs(ar[:,:,:3][core]-reference[:,:,:3][core]).mean())}
canvas.save(folder/'comparison.png')
grid=Image.new('RGB',(800,490),'#171b21');crop=ref.crop(box).resize((800,450),Image.Resampling.NEAREST);grid.paste(crop,(0,40),crop);g=ImageDraw.Draw(grid)
for x in range(300,691,25):
    px=(x-box[0])*2;g.line((px,40,px,490),fill='#5b6066',width=1);g.text((px+2,12),str(x),fill='white')
for y in range(425,631,25):
    py=40+(y-box[1])*2;g.line((0,py,800,py),fill='#5b6066',width=1);g.text((3,py+2),str(y),fill='white')
grid.save(folder/'reference-grid.png')
(folder/'diagnostic-metrics.json').write_text(json.dumps({'crop':box,'scores':scores,
 'reference_sha256':hashlib.sha256((ROOT/'assets/bishop/reference.png').read_bytes()).hexdigest(),
 'note':'Unsaved cropped diagnostic comparisons only. Bright reference core is fixed at R>210, G>150, B>70; it is not a mission score or replacement outline mask.'},indent=2)+'\n')
print(json.dumps(scores,indent=2))
