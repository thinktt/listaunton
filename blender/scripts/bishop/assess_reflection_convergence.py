"""Compare actual rendered slit crops at their unchanged pixel coordinates."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();out=ROOT/a.directory
m=json.loads((out/'manifest.json').read_text());samples=m['samples']
reference=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGB'),dtype=np.float64)
yy,xx=np.mgrid[:reference.shape[0],:reference.shape[1]];tip=((xx-497)/15)**2+((yy-430)/12)**2<1;core=tip&(reference[:,:,1]>245)
images=[reference];records=[]
for n in samples:
    ar=np.array(Image.open(out/f'samples-{n}.png').convert('RGB'),dtype=np.float64);images.append(ar)
    records.append({'samples':n,'tip_error':float(np.abs(ar-reference)[tip].mean()),'core_error':float(np.abs(ar-reference)[core].mean()),'core_mean_rgb':ar[core].mean(0).tolist()})
delta=np.abs(images[-1]-images[-2]);report={'renders':records,'last_pair_tip_mean_change':float(delta[tip].mean()),'last_pair_tip_p99_change':float(np.quantile(delta[tip],.99)), 'note':'Convergence diagnostic, not a proof of exact reference match.'}
(out/'statistics.json').write_text(json.dumps(report,indent=2)+'\n')
canvas=Image.new('RGB',(400*len(images),430),'#161b20');d=ImageDraw.Draw(canvas)
for i,(label,ar) in enumerate(zip(['Reference']+[str(n)+' fixed samples' for n in samples],images)):
    tile=Image.fromarray(ar.astype('uint8')).crop((455,390,555,475)).resize((400,340),Image.Resampling.NEAREST);canvas.paste(tile,(i*400,65));d.text((i*400+12,20),label,fill='white')
canvas.save(out/'comparison.png');print(json.dumps(report,indent=2))
