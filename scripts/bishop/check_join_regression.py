"""Show that evaluated side-section sampling detects the rejected exposed neck."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path(__file__).resolve().parents[2]
cfg=json.loads((root/'scripts/bishop/profile.json').read_text(encoding='utf-8'))
A=json.loads((root/'assets/bishop/original-alignment.json').read_text(encoding='utf-8'))
factor=1254/300/A['scale']/cfg['scale'];co=math.cos(math.radians(cfg['elevation']))
report={}
for label,path in [('rejected_neck','history/bishop/07-before-continuous-button-join/bishop-rebuilt.blend'),('current','models/bishop/bishop-rebuilt.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(root/path));graph=bpy.context.evaluated_depsgraph_get()
 objects=[bpy.data.objects[name].evaluated_get(graph) for name in ['Bishop - continuous turned body','Bishop - domed button finial']]
 radius=[];step=.01
 shift=cfg.get('shared_turning',{}).get('upper_axis_offset',0.)
 if label=='current':
  refit=cfg.get('side_refit',{})
  scale=refit.get('axis_slope',1.)
  offset=refit.get('axis_offset',shift)
  start=59*scale+offset
  end=min(54*scale+offset,cfg['head_button_join']['head_cap_axis_y']-.4*scale)
 else:
  benchmark=cfg
  if cfg.get('side_refit'):
   spec=json.loads((root/cfg['side_refit']['config']).read_text())
   benchmark=json.loads((root/spec['source_profile']).read_text())
  source_shift=benchmark.get('shared_turning',{}).get('upper_axis_offset',0.)
  start,end=59.,min(54.,benchmark['head_button_join']['head_cap_axis_y']-source_shift-.4)
 count=math.ceil((start-end)/step)+1
 for i in range(count):
  axis_y=start-i*step;z=(cfg['y0']-axis_y)*factor/co;r=[]
  for ob in objects:
   hit,loc,normal,face=ob.ray_cast(Vector((-4,0,z)),Vector((1,0,0)),distance=8)
   if hit:r.append(-loc.x/factor)
  assert r,('Gap in external side section',label,axis_y)
  radius.append(max(r))
 run=longest=0
 for a,b in zip(radius,radius[1:]):
  # Inspect the complete external surface. The historical bad seat was part
  # of the button object, so filtering to the head would hide the defect.
  run=run+1 if abs(co*(a-b)/step)<.05 else 0
  longest=max(longest,run)
 report[label]={'samples':len(radius),'sample_axis_y_range':[start,end],
                'maximum_nearly_cylindrical_run_in_original_axis_units':longest*step}
assert report['rejected_neck']['maximum_nearly_cylindrical_run_in_original_axis_units']>.5,'Regression fixture no longer reproduces the rejected neck.'
assert report['current']['maximum_nearly_cylindrical_run_in_original_axis_units']<.1,'Current model exposes a cylindrical neck.'
report['passed']=True
(root/'assets/bishop/join-regression.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
