"""Retain the walnut figure while bringing the descending blade toward the rear billet."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path(__file__).resolve().parent
def raster(t):
    low=np.floor(t.min(0)).astype(int);high=np.ceil(t.max(0)).astype(int)
    if np.any(high<0) or np.any(low>3071):return None
    low=np.maximum(0,low);high=np.minimum(3071,high)
    yy,xx=np.mgrid[low[1]:high[1]+1,low[0]:high[0]+1]
    q=np.stack((xx+.5,yy+.5),-1)-t[0]
    a=t[1]-t[0];b=t[2]-t[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1e-9:return None
    u=(q[...,0]*b[1]-q[...,1]*b[0])/det;v=(a[0]*q[...,1]-a[1]*q[...,0])/det
    ok=(u>=0)&(v>=0)&(u+v<=1)
    if not ok.any():return None
    return yy[ok],xx[ok],np.stack((1-u[ok]-v[ok],u[ok],v[ok]),-1)

def main():
    im=Image.open(D/'parent-pigment.png').convert('RGB')
    W,H=im.size;data=np.load(D/'atlas-geometry.npz');name='swept rounded mane'
    weights=data['strength'];p=Image.new('L',(W,H));pen=ImageDraw.Draw(p)
    for key in data.files:
        if key in (name,'strength'):continue
        tris=data[key]*[W,-H]+[0,H]
        for tri in tris:pen.polygon([tuple(q) for q in tri],fill=255)
    protected=np.asarray(p.filter(ImageFilter.MaxFilter(5)))>0
    field=np.zeros((H,W),np.float32);occupied=np.zeros((H,W),bool)
    for t,w in zip(data[name]*[W,-H]+[0,H],weights):
        if w.max()<.0001:continue
        r=raster(t)
        if r is None:continue
        yy,xx,b=r;field[yy,xx]=np.maximum(field[yy,xx],b@w);occupied[yy,xx]=True
    overlap=int((occupied&protected).sum())
    for _ in range(2):
        joint=field.copy()
        for delta in [(1,0),(-1,0),(0,1),(0,-1)]:joint=np.maximum(joint,np.roll(field,delta,(0,1)))
        field=joint
    field[protected]=0
    raw=np.asarray(im);q=raw.astype(np.float32)
    stats={'protected_pixels_at_affected_mane':overlap,'affected_mane_pixels':int(occupied.sum()),
           'physical_field':'Long bilateral blade face in native rest coordinates. Broad stain is invariant to viewing and illumination.'}
    for name,gain in [('satin',.69),('light',.76),('deep',.64)]:
        target=np.uint8(np.clip(np.round(q*(1+(gain-1)*field[:,:,None])),0,255))
        file=D/f'pigment-{name}.png';Image.fromarray(target).save(file,compress_level=5)
        changed=np.any(raw!=target,axis=2)
        stats[name]={'gain':gain,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'changed_texels':int(changed.sum()),
                     'changed_protected_texels':int((changed&protected).sum()),'max_channel_delta':int(abs(target.astype(np.int16)-raw).max())}
    (D/'pigment-probe.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
if __name__=='__main__':main()
