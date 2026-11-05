"""Inspect the evaluated lathe section for hidden local profile crossings."""
from pathlib import Path
import argparse,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
def inspect(source):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/source),load_ui=False);body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'body' in o.name and not o.get('king_render_region'))
    control=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
    bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();co=np.array([v.co[:] for v in mesh.vertices]);keep=(abs(co[:,1])<1e-7)&(co[:,0]>.9)&(co[:,2]<.6)
    edges=[list(e.vertices) for e in mesh.edges if all(keep[i] for i in e.vertices)];segments=[co[p][:,[0,2]].tolist() for p in edges];crossings=[]
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    for i,(a,b) in enumerate(segments):
        a=np.array(a);d=np.array(b)-a
        for j,(c,e) in enumerate(segments[i+1:],i+1):
            if set(edges[i])&set(edges[j]):continue
            c=np.array(c);v=np.array(e)-c;den=cross(d,v)
            if abs(den)<1e-14:continue
            t=cross(c-a,v)/den;u=cross(c-a,d)/den
            if 1e-6<t<1-1e-6 and 1e-6<u<1-1e-6:crossings.append({'edges':[i,j],'radius_z':(a+t*d).tolist()})
    ev.to_mesh_clear()
    return {'source':source,'section':'positive X, y=0, radius>0.9 and z<0.6','segments':segments,'crossings':crossings,'control_profile':[[i,float(np.linalg.norm(row[:,:2],axis=1).mean()),float(row[:,2].mean())] for i,row in enumerate(control) if i<17]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report={'before':inspect(a.before),'after':inspect(a.after)};out=ROOT/a.output;out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:{'segments':len(v['segments']),'crossings':v['crossings']} for k,v in report.items()},indent=2))
