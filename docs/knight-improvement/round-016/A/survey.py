"""Inspect true native control ring locations and 54-degree contacts on the parent."""
from pathlib import Path
import json,sys,hashlib
import bpy,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from lower_carving_fit import rest_coords
from mission_scene import world_vertices,sha
from probe_carving import point_probe,rest
def run(name):
 src=D/(name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False);s=bpy.context.scene
 p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ['dx','dy','twist_degrees']]
 ob=s.objects['Knight | swept rounded mane'];v=world_vertices(ob);print('vertices',len(v),[(m.name,m.type,m.levels,m.render_levels) for m in ob.modifiers],flush=True)
 # First 832 native vertices retain the longitudinal control-ring order following committed subdivision.
 raw=rest_coords(v[:832],pose).reshape(-1,64,3)
 uv=np.array([world_to_camera_view(s,s.camera,Vector(pt)) for pt in v[:832]]).reshape(-1,64,3)
 pix=uv[:,:,:2]*[1254,-1254]+[0,1254]
 attr=ob.data.attributes['Knight varnish coverage'];wax=np.empty(len(v),np.float32);attr.data.foreach_get('value',wax);wax=wax[:832].reshape(-1,64)
 rings=[]
 for i,row in enumerate(raw):
  points={j:[np.round(row[j],4).tolist(),np.round(pix[i,j],1).tolist(),round(float(wax[i,j]),3)] for j in [0,16,18,22,24,25,26,27,28,30,32,36,38,39,40,42,46,48]}
  rings.append(points);print('ring',i,'inner',points[0][:2],'top',points[32][:2],'near bevel',points[39][:2])
 probe=point_probe(s);samples=[]
 for x in [300,320,345,365,385,405,425,435,445,455,460,465,470,475,480,485,490]:
  gy=np.interp(x,[300,320,345,365,385,405,425,435,445,455,460,465,470,475,480,485,490],[346,342,338,337,337,337,340,343,345,349,351,354,357,364,371,379,385])
  for dy in [-15,-5,0,5,14]:
   y=round(gy+dy);q=probe(x+.5,y+.5)
   if q:samples.append([x,y,q[1],np.around(rest(q[2],p),4).tolist(),np.around(q[3],4).tolist()])
 lights={o.name:{'position':list(o.location),'energy':o.data.energy,'size':o.data.size,'height':o.data.size_y,'color':list(o.data.color),'receivers':o.light_linking.receiver_collection.name if o.light_linking.receiver_collection else None} for o in s.objects if o.type=='LIGHT'}
 (D/(name+'-surface.json')).write_text(json.dumps({'sha':sha(src),'rings':rings,'samples':samples,'lights':lights},indent=2)+'\n')
if __name__=='__main__':run(sys.argv[-1] if sys.argv[-1] in ['parent','knight','inspection'] else 'parent')
