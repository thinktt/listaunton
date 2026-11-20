from pathlib import Path
import sys,json,math,bpy,numpy as np
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from survey import chart
from mission_scene import world_vertices
from lower_carving_fit import rest_coords
bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene;p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ['dx','dy','twist_degrees']]
for n in ['near swept ear','near eye']:
 ob=s.objects['Knight | '+n];xyz=rest_coords(world_vertices(ob),pose);u,v=chart(xyz).T
 for a in [-.34,-.25,-.15,-.05,.05,.15,.25,.35]:
  use=np.flatnonzero(abs(u-a)<.035)
  if len(use):print(n,a,len(use),np.round(np.percentile(v[use],[0,25,50,75,100]),3),np.round(np.percentile(abs(xyz[use,1]),[0,25,50,75,100]),3))
