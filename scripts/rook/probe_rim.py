from pathlib import Path
import bpy,sys,json,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/rook'))
from render_regions import closed_body
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'history/rook-mission-025/models/rook/rook-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;b=closed_body(s);dg=bpy.context.evaluated_depsgraph_get();ev=b.evaluated_get(dg);m=ev.to_mesh()
report={'objects':[]}
for o in s.objects:
 if o.type!='MESH':continue
 mods=[]
 for mod in o.modifiers:
  mods.append({'name':mod.name,'type':mod.type,**{k:getattr(mod,k) for k in ['width','segments','harden_normals','keep_sharp','weight'] if hasattr(mod,k)}})
 report['objects'].append({'name':o.name,'receiver':o.get('rook_render_receiver'),'mods':mods,'bounds_z':[min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)]})
rows=[]
for p in m.polygons:
 if p.center.z<2.68:continue
 ns=[m.corner_normals[i].vector for i in p.loop_indices]
 rows.append({'center':list(p.center),'normal':list(p.normal),'corner_z':[n.z for n in ns],'smooth':p.use_smooth,'area':p.area})
report['top_faces']=rows
out=ROOT/'build/rook-mission/030-rim-normal-probe';out.mkdir(exist_ok=True,parents=True)
(out/'probe.json').write_text(json.dumps(report,indent=2))
print('OBJECTS',json.dumps(report['objects']))
for low,high in [(-1,-.1),(-.1,.1),(.1,.4),(.4,.8),(.8,.98),(.98,1.01)]:
 select=[r for r in rows if low<=r['normal'][2]<high]
 print('NORMAL_BIN',low,high,'faces',len(select),'area',sum(r['area'] for r in select),'corner_z',sorted({round(z,3) for r in select for z in r['corner_z']})[:25])
ev.to_mesh_clear()
