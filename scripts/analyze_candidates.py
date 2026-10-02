"""Measure silhouettes; write browser placements only. Never rewrite image pixels."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
N=180
generated=json.loads((root/'assets/candidates/generation.json').read_text(encoding='utf-8'))['records']
candidate_files={(r['piece'],r['candidate']):r['file'] for r in generated}
def mask(path):
    im=Image.open(path).convert('RGBA');size=im.size
    ar=np.array(im.resize((N,N),Image.Resampling.BILINEAR))
    m=(ar[:,:,:3].max(2)>12)&(ar[:,:,3]>127)
    return m,size
def bounds(m):
    y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def fit(source,target):
    a,b=bounds(source),bounds(target)
    scale=(b[3]-b[1])/(a[3]-a[1]);tx=(b[0]+b[2]-scale*(a[0]+a[2]))/2;ty=(b[1]+b[3]-scale*(a[1]+a[3]))/2
    yy,xx=np.indices((N,N))
    def score(s,x,y):
        sx=np.rint((xx-x)/s).astype(int);sy=np.rint((yy-y)/s).astype(int)
        inside=(sx>=0)&(sy>=0)&(sx<N)&(sy<N)
        projected=source[np.clip(sy,0,N-1),np.clip(sx,0,N-1)]&inside
        return np.count_nonzero(projected&target)/np.count_nonzero(projected|target)
    best=score(scale,tx,ty)
    for step in [2,1,.4,.15]:
        for _ in range(12):
            improved=False
            for ds,dx,dy in [(step/N,0,0),(-step/N,0,0),(0,step,0),(0,-step,0),(0,0,step),(0,0,-step)]:
                trial=(scale+ds,tx+dx,ty+dy);v=score(*trial)
                if v>best:scale,tx,ty=trial;best=v;improved=True
            if not improved:break
    return dict(scale=scale,x=tx/N*100,y=ty/N*100,silhouette_iou=best)
result={'method':'Uniform scale and translation fitted to the black original silhouette at 180px; no shape warping. White knight mirrored only in aligned view.','pieces':{}}
for piece in ['king','rook','bishop','knight','pawn']:
    target,size=mask(root/f'references/lichess-staunton-3d/Black-{piece.title()}.png')
    items=[]
    for key,label,file in [('black','Original black',f'references/lichess-staunton-3d/Black-{piece.title()}.png'),('white','Original white',f'references/lichess-staunton-3d/White-{piece.title()}.png')]+[(f'candidate-{n}',f'Candidate {n}',candidate_files[(piece,n)]) for n in range(1,4)]:
        m,size=mask(root/file);flip=piece=='knight' and key=='white'
        if flip:m=m[:,::-1]
        placement=fit(m,target) if key!='black' else dict(scale=1,x=0,y=0,silhouette_iou=1)
        items.append(dict(id=key,label=label,file=file,width=size[0],height=size[1],flip=flip,**placement))
    result['pieces'][piece]=items
    print(piece,[(v['id'],round(v['silhouette_iou'],3),[v['width'],v['height']]) for v in items])
(root/'assets/candidates/alignment.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
