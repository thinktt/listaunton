"""Find crossings in the complete positive-X evaluated lathe section."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);body=next(o for o in controls(bpy.context.scene) if 'body' in o.name)
control=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
profile=np.array([[np.linalg.norm(row[:,:2],axis=1).mean(),row[:,2].mean()] for row in control])
for m in body.modifiers:
    if m.type=='SUBSURF':m.levels=m.render_levels
bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
co=np.array([v.co[:] for v in mesh.vertices]);keep=(abs(co[:,1])<1e-7)&(co[:,0]>1e-7)
edges=[list(e.vertices) for e in mesh.edges if all(keep[i] for i in e.vertices)]
segments=[co[p][:,[0,2]] for p in edges];crossings=[]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
for i,(start,end) in enumerate(segments):
    d=end-start
    for j,(c,e) in enumerate(segments[i+1:],i+1):
        if set(edges[i])&set(edges[j]):continue
        v=e-c;den=cross(d,v)
        if abs(den)<1e-14:continue
        t=cross(c-start,v)/den;u=cross(c-start,d)/den
        if 1e-6<t<1-1e-6 and 1e-6<u<1-1e-6:
            point=start+t*d;nearest=np.argsort(np.linalg.norm(profile-point,axis=1))[:8]
            crossings.append(dict(edges=[i,j],radius_z=point.tolist(),nearest_controls=[[int(k),*profile[k].tolist()] for k in nearest]))
ev.to_mesh_clear();assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report=dict(source=a.source,source_sha256=digest,segment_count=len(segments),crossings=crossings,control_profile=profile.tolist())
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('FULL_PROFILE_CROSSINGS',json.dumps(crossings),flush=True)
