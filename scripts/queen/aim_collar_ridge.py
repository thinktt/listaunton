"""Aim real middle-collar lights at the measured reference reflection ridge."""
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/152-complete-collar-fill/queen.blend'
capture=ROOT/'build/queen-mission/collar-surface-148'
positions=np.load(capture/'position.npy');normals=np.load(capture/'normal.npy')
ridge=json.loads((capture/'reference-ridge.json').read_text());byname={p['name']:p for p in ridge}
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cfg=json.loads(s['mission_material_config'])
view=s.camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize();targets=[]
for spec in cfg['lights']:
 if spec['name'] not in byname:continue
 light=bpy.data.objects[spec['name']];point=byname[spec['name']];tx,ty=point['ridge_pixel'];xx,yy=tx-290,ty-350
 loc=Vector(positions[yy,xx,:3]);local=[]
 assert positions[yy,xx,3]>.999 and 2.97<loc.z<3.16
 for qy in range(yy-1,yy+2):
  for qx in range(xx-1,xx+2):
   if positions[qy,qx,3]>.999 and 2.97<positions[qy,qx,2]<3.16 and np.linalg.norm(positions[qy,qx,:3]-np.array(loc))<.03:local.append(normals[qy,qx,:3])
 normal=Vector(np.mean(local,axis=0));normal.normalize();assert normal.dot(view)>.03
 direction=2*normal.dot(view)*normal-view;pos=loc+direction*6
 light.location=pos;light.rotation_euler=(loc-pos).to_track_quat('-Z','Y').to_euler()
 spec.update(position=list(pos),target=list(loc),initial_target_pixel=spec['target_pixel'],target_pixel=[tx,ty],surface_pixel=[tx,ty],surface_normal=list(normal))
 targets.append({'name':light.name,'initial_pixel':point['old'],'surface_pixel':[tx,ty],'normal_samples':len(local),'target_z':loc.z,'normal':list(normal)})
cfg['collar_reference_ridge']={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'targets':targets,'measurement':ridge,'method':'Peak of a three-pixel horizontal median of minimum reference RGB, within a fixed +/-16-pixel vertical corridor and the visible middle-collar surface. No pixel or camera registration edits. Aim from measured native surface positions and textured normals.'}
cfg['variant']='154-measured-collar-ridge';s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('REFERENCE_RIDGE_AIMED',flush=True)
