from pathlib import Path
import json,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_scene import world_vertices
from probe_carving import point_probe
from evidence import load
ax=np.array([1.,-.76])/np.hypot(1.,.76);up=np.array([-ax[1],ax[0]])
def chart(a):
    q=a[:,[0,2]]-[.412,4.158]
    return q@ax,q@up
def go():
    s=load('parent.blend');pose=json.loads(s['knight_mission_pose'])
    p=[pose[k] for k in ('dx','dy','twist_degrees')]
    data={};rays=point_probe(s)
    for name in ['near eye','far eye','continuous horse head and neck']:
        ob=s.objects['Knight | '+name];r=rest_coords(world_vertices(ob),p)
        u,v=chart(r);mask=(abs(u)<.42)&(abs(v)<.21)
        a=np.empty(len(r),np.float32);ob.data.attributes['Knight varnish coverage'].data.foreach_get('value',a)
        data[name]={'native_count':len(r),'points':r[mask].tolist(),'finish':a[mask].tolist(),
                  'modifiers':[(m.name,m.type,getattr(m,'levels',None)) for m in ob.modifiers]}
        print(name,len(r),ob.data.name,data[name]['modifiers'])
        if name.endswith('eye'):
            print('bounds(R)',np.round(r.min(0),4),np.round(r.max(0),4),'UV',np.round([u.min(),u.max(),v.min(),v.max()],3),'var',np.percentile(a,[0,50,100]))
    data['rays']=[]
    for y in range(461,511,2):
        for x in range(464,555,2):
            h=rays(x+.5,y+.5)
            if h:
                arr=rest_coords(np.array([list(h[2])]),p);u,v=chart(arr)
                data['rays'].append([x,y,h[1].split(' | ')[-1],*arr[0],u[0],v[0]])
    (D/'orbital-parent.json').write_text(json.dumps(data,separators=(',',':')))
    print('ref_points')
    for x,y in [(482,474),(492,476),(504,478),(512,480),(520,482),(530,486),(508,484),(516,487),(526,490),(535,488),(504,498)]:
        h=rays(x+.5,y+.5);arr=rest_coords(np.array([list(h[2])]),p);u,v=chart(arr)
        print(x,y,h[1],np.round([u[0],v[0]],3))
    for light in s.objects:
        if light.type=='LIGHT' and any(k in light.name.lower() for k in ('eye','cheek','lid')):
            print(light.name,light.data.energy,light.data.shape,light.data.size,light.data.size_y)
if __name__=='__main__':go()
