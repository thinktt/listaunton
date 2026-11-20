"""Measure the posed eye, the ear that overhangs it, and both native surfaces."""
from pathlib import Path
import json,sys
import numpy as np,bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from orbital import get_surface,rest_coords,pose,chart,probe as skull_probe
from evidence import load
from probe_carving import point_probe
def run(key):
    s=load(key+'.blend');p=pose(s);u,v,a=get_surface(s)
    np.savez_compressed(D/f'field-{key}.npz',u=u,v=v,surfaces=a);point=point_probe(s)
    source=json.loads((D/'upper-source.json').read_text())['results']['Black 2']['trace']
    rows=source[::4]+[[503,480],[504,473],[505,472],[526,484],[536,482],[503,487],[501,489]]
    def physical(x,y):
        hit=point(x+.5,y+.5)
        if not hit:return
        xyz=rest_coords(np.asarray(hit[2])[None,:],p);uu,vv=chart(xyz)
        return [x,y,hit[1].removeprefix('Knight | '),round(float(uu[0]),5),round(float(vv[0]),5),round(float(abs(xyz[0,1])),5)]
    data=[physical(x,y) for x,y in rows]
    print(data,flush=True)
    skull=skull_probe(s,source);sample=np.array(source)
    def curve(si):
        h,e=a[si];mask=e>h;n=np.flatnonzero(mask.any(0));vi=np.array([np.flatnonzero(mask[:,i])[[0,-1]] for i in n])
        return np.column_stack([u[n],v[vi[:,0]],v[vi[:,1]]])
    for i in [0,1]:
        points=curve(i);print(i,points[::9].round(4).tolist())
    (D/f'survey-{key}.json').write_text(json.dumps({'visible_hits':data,'underlying_skull_at_source_upper':skull},indent=2)+'\n')
if __name__=='__main__':run(sys.argv[-1])
