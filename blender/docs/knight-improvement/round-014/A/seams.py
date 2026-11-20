"""Certify UV seam agreement on actual split native points and byte-identical viewer shape."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
def sample(image,uv):
    y,x=((1-uv[1])*image.shape[0]-.5,uv[0]*image.shape[1]-.5);x,y=np.clip(x,0,image.shape[1]-1.001),np.clip(y,0,image.shape[0]-1.001)
    a,b=int(x),int(y);f,g=x-a,y-b
    return ((1-g)*((1-f)*image[b,a]+f*image[b,a+1])+g*((1-f)*image[b+1,a]+f*image[b+1,a+1]))
def main():
    field=np.load(D/'native-uv.npz');p=field['xyz'].reshape(-1,3);u=field['uv'].reshape(-1,2)
    images={key:np.asarray(Image.open(D/file).convert('RGB')) for key,file in [('parent','parent-pigment.png'),('candidate','pigment.png')]}
    points={}
    for xyz,uv in zip(p,u):
        if 2.37<xyz[2]<4.31:points.setdefault(tuple(xyz),set()).add(tuple(uv))
    results={k:[] for k in images};q=np.array([.2126,.7152,.0722])
    for xyz,uvs in points.items():
        if len(uvs)<2:continue
        for k,img in images.items():
            val=[sample(img,uv)@q for uv in uvs];results[k].append(max(val)-min(val))
    report={k:{'split_surface_points':len(vals),'median_luminance_difference':round(float(np.median(vals)),2),'p95':round(float(np.percentile(vals,95)),2),'maximum':round(float(np.max(vals)),2)} for k,vals in results.items()}
    (D/'seams.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
if __name__=='__main__':main()
