from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'scripts/pawn'))
from lathe_projection import visible_tiles
from derive_wood import ramp
g=r/'build/pawn-mission/pigment-060';profile=np.load(g/'meridian.npy');depth=np.load(g/'depth.npy')[:,:,0]
c=json.loads((r/'assets/pawn/camera.json').read_text());f=np.asarray(Image.open(r/'assets/pawn/pawn-varnish-v7.png'))
n=np.asarray(Image.open(r/'assets/pawn/pawn-fine-slopes-v7.png'));size=len(f)
points=[(393,642),(400,633),(407,625),(416,616),(414,627),(421,616),(406,640),(407,651)]
best={xy:(100,None) for xy in points}
for rows,x,y,z,px,py,vis in visible_tiles(profile,depth,c,size):
    for xy in points:
        d=(px-xy[0])**2+(py-xy[1])**2;d[vis<.5]=1e9
        i,j=np.unravel_index(d.argmin(),d.shape)
        if d[i,j]<best[xy][0]:
            row=int(rows[i]);v=1-(row+.5)/size
            band=float(ramp(np.array(v),.422,.44)*(1-ramp(np.array(v),.646,.668)))
            best[xy]=(float(d[i,j]),{'uv':[float((j+.5)/size),v],'row_col':[row,int(j)],'height':float(z[i,0]),'visibility':float(vis[i,j]),'focus':band,'rough':float(.3+2.1*f[row,j,0]/255),'polish':float(.38+1.47*f[row,j,1]/255),'slopes':((n[row,j,:2].astype(float)-128)*.135/127).tolist()})
result={str(k):v for k,v in best.items()}
(r/'build/pawn-mission/076-stem-coordinates.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
