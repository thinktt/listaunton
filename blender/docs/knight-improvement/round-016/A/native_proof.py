"""Record actual rest-frame extents, protected wood, fixed camera, upper facet sections and their mirrored pairs."""
from pathlib import Path
import json,hashlib,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from sculpt import load,pose,rest_coords,world_vertices,sha
from mission_scene import visible_meshes
def protect(name):
 s=load(name);p=pose(s);parts={};G=np.load(D/'ring-chart.npz')['grid']
 for ob in visible_meshes(s):
  m=ob.data;pos=rest_coords(world_vertices(ob),p);uv=np.empty((len(m.loops),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
  varn=np.empty(len(m.vertices),np.float32);m.attributes['Knight varnish coverage'].data.foreach_get('value',varn)
  part={'vertices':len(pos),'xyz':hashlib.sha256(pos.tobytes()).hexdigest(),'uv':hashlib.sha256(uv.tobytes()).hexdigest(),'varnish':hashlib.sha256(varn.tobytes()).hexdigest()}
  parts[ob.name]=part
  if ob.name.endswith('rounded mane'):v=pos
  if ob.name.endswith('continuous horse head and neck'):skin=pos
 cam=s.camera;rig={o.name:[np.array(o.matrix_world).round(7).tolist(),list(o.data.color),o.data.energy,o.data.size,o.data.size_y,o.data.spread] for o in s.objects if o.type=='LIGHT'}
 return {'sha':sha(D/(name+'.blend')),'parts':parts,'camera':[np.array(cam.matrix_world).tolist(),cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y],'lights':rig},v,skin,G
old,b,s0,G=protect('parent');new,a,s1,_=protect('knight');delta=np.linalg.norm(a-b,axis=1)
shelter=(s0[:,0]<=-.08)|(s0[:,0]>=.40)|(abs(s0[:,1])>=.405)|(s0[:,2]<=4.83)
checks={'parent':old['sha'],'model':new['sha'],'identical_parts':[k for k in old['parts'] if old['parts'][k]==new['parts'][k]],'identical_uvs':all(old['parts'][k]['uv']==new['parts'][k]['uv'] for k in old['parts']),'changed_studio_lights':[k for k in new['lights'] if new['lights'][k]!=old['lights'].get(k)],'same_camera':new['camera']==old['camera'],'skull_vertices_outside_edit':int(shelter.sum()),'skull_outside_edit_max_displacement':float(np.linalg.norm(s1[shelter]-s0[shelter],axis=1).max()),'mane_station_3_75_through_12_max_displacement':float(delta[G[15:]].max()),'maximum_mane_displacement':float(delta.max()),'maximum_forehead_displacement':float(np.linalg.norm(s0-s1,axis=1).max()),'all_parent_vertices':sum(q['vertices'] for q in old['parts'].values())}
def section(verts,station):
 row=verts[G[station]];ray=row[128,[0,2]]-row[0,[0,2]];ray/=np.linalg.norm(ray)
 idx=128+np.arange(0,65);y=abs(row[idx,1]);r=(row[idx][:,[0,2]]-row[128,[0,2]])@ray
 slopes=(r[1:]-r[:-1])/(y[1:]-y[:-1]);mid=abs(row[128:193] - row[128-np.arange(65)]*[1,-1,1])
 return {'station':station/4,'physical_bevel_lateral_width':round(float(y[32]-y[24]),5),'bevel_normal_turn_degrees':round(float(abs(np.degrees(np.arctan(slopes[32])-np.arctan(slopes[23])))),2),'underface_slope_magnitudes':[round(float(-slopes[j]),2) for j in [32,36,40,44,48,52,56]],'bilateral_max_xyz_difference':float(mid.max()),'y':y.tolist(),'r':r.tolist()}
checks['parent_sections']=[section(b,i) for i in [4,6,8,10,12]];checks['sections']=[section(a,i) for i in [4,6,8,10,12]]
(D/'native-proof.json').write_text(json.dumps(checks,indent=2)+'\n')
print({k:v for k,v in checks.items() if 'sections' not in k},flush=True)
