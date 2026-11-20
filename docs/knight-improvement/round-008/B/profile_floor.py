"""Locate where the accepted turned base takes over the front outline."""
from pathlib import Path
import json
import numpy as np

OUT=Path(__file__).resolve().parent
def horizontal_limits(bundle,name,rows):
    desc=json.loads((bundle/'mesh.json').read_text())
    cam=desc['referenceCamera']
    view=np.asarray(cam['worldToCamera']).reshape(4,4)
    proj=np.asarray(cam['projectionMatrix']).reshape(4,4)
    transform=proj@view
    part=next(p for p in desc['parts'] if p['name'].endswith(name))
    raw=(bundle/'mesh.bin').read_bytes()
    vertices=np.frombuffer(raw,dtype='<f4',count=desc['vertexByteLength']//4).reshape(-1,desc['vertexStrideBytes']//4)
    ind=np.frombuffer(raw,dtype='<u4',offset=desc['indexByteOffset'])[part['indexOffset']:part['indexOffset']+part['indexCount']].reshape(-1,3)
    screens=vertices[:,:3]@transform[:2,:3].T+transform[:2,3]
    screens=(np.array([1,-1])*screens+1)*.5*cam['width']
    triangles=screens[ind]
    low=triangles[:,:,1].min(1)
    high=triangles[:,:,1].max(1)
    limits={}
    for y in rows:
        z=y+.5
        crossing=triangles[(low<z)&(high>z)]
        current=[]
        for i in range(3):
            a=crossing[:,i]
            b=crossing[:,(i+1)%3]
            cut=(a[:,1]-z)*(b[:,1]-z)<0
            a,b=a[cut],b[cut]
            if len(a):current.append(np.max(a[:,0]+(z-a[:,1])/(b[:,1]-a[:,1])*(b[:,0]-a[:,0])))
        if current:limits[y]=round(float(max(current)),2)
    return limits
if __name__=='__main__':
    rows=range(540,681)
    parts=['turned pedestal','continuous horse head and neck']
    folder=OUT.parents[2]/'assets/knight'
    data={'parent':{part:horizontal_limits(folder,part,rows) for part in parts}}
    candidate=OUT/'review-copy/assets/knight'
    if (candidate/'mesh.json').exists():
        data['B']={part:horizontal_limits(candidate,part,rows) for part in parts}
    (OUT/'part-profiles.json').write_text(json.dumps(data,indent=2)+'\n')
    for y in range(595,666,5):
        print(y,[data['parent'][p].get(y) for p in parts])
