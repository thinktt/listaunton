"""Layer the separate chest and pedestal pigment studies and record their disjoint support."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
from PIL import Image
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base,chest,pedestal,out=map(lambda p:Path(p).resolve(), sys.argv[1:5])
    strength=float(sys.argv[5])
    assert 0<strength<=1
    rgb=lambda p:np.asarray(Image.open(p).convert('RGB'))
    parent,warm,grain=map(rgb,(base,chest,pedestal))
    changed=np.any(grain!=parent,axis=2)
    assert not np.any(changed & np.any(warm!=parent,axis=2))
    joined=warm.copy()
    joined[changed]=np.round((1-strength)*parent[changed]+strength*grain[changed]).astype('uint8')
    out.mkdir(parents=True,exist_ok=True)
    Image.fromarray(joined).save(out/'pigment.png')
    stats={'parent':sha(base),'chest':sha(chest),'pedestal':sha(pedestal),'pedestal_display_blend':strength,
           'overlapping_edits':0,'texture':sha(out/'pigment.png')}
    (out/'pigment.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(stats)
if __name__=='__main__':main()
