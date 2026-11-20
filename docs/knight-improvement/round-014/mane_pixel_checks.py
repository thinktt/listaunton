"""Check that the contours and clay views survive the mane wood treatment."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
b=root/'build/knight-mission';j=b/f'round-{n:03}-judge'
assets=root/'assets/knight'
def rgba(path):
    with Image.open(path) as im:return np.asarray(im.convert('RGBA'),dtype=np.int16)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def error(a,b,mask):
    delta=np.abs(a[mask,:3]-b[mask,:3])
    return {'mean':round(float(delta.mean()),4),'p95':float(np.percentile(delta,95)),'max':int(delta.max())}

record={}
for k in labels:
    trial=b/f'improvement-{n:03}-{k}'
    views={}
    for name,p,q in [('fixed',assets/'render.png',trial/'wood.png'),('side',assets/'guide-render.png',trial/'wood-side.png')]:
        parent=rgba(p);candidate=rgba(q)
        assert parent.shape==candidate.shape
        inside=(candidate[:,:,3]>245)&(parent[:,:,3]>245)
        item={'parent':sha(p),'candidate':sha(q),'changed_alpha_pixels':int((parent[:,:,3]!=candidate[:,:,3]).sum()),
              'all_foreground_color_change':error(parent,candidate,inside)}
        if name=='fixed':
            rois={'eye':(460,455,560,508),'head of muzzle':(580,455,718,510),'mane face':(188,463,280,621)}
            for label,(x0,y0,x1,y1) in rois.items():
                sl=np.s_[y0:y1,x0:x1]
                item[label]=error(parent[sl],candidate[sl],inside[sl])
        views[name]=item
    stats={}
    for f in ('clay','back','mane-passes'):
        parent=j/f'{f}-parent';other=j/f'{f}-{k}'
        for path in parent.glob('*.png'):
            if f=='back' and not path.name.startswith('clay-'):continue
            if f=='mane-passes' and path.name!='polish.png':continue
            a=rgba(path);c=rgba(other/path.name);inside=(a[:,:,3]>252)&(c[:,:,3]>252)
            stats[f+'/'+path.name]=error(a,c,inside)
    record[k]={'source':sha(trial/'knight.blend'),'register':views,'neutral_color_comparisons':stats}
(j/'unchanged-carving.json').write_text(json.dumps(record,indent=2)+'\n')
for k,v in record.items():
    print(k,{t:d['changed_alpha_pixels'] for t,d in v['register'].items()},'largest clay mean RGB difference',max(d['mean'] for d in v['neutral_color_comparisons'].values()),'eye',v['register']['fixed']['eye'])
