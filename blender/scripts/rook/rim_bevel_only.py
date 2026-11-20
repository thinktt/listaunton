"""Split existing rim receiver without moving its surface; restrict new lights to upper bevels."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));sys.path.insert(0,str(ROOT/'scripts/rook'))
from mission_trial import gpu
import importlib.util
spec=importlib.util.spec_from_file_location('rook_regions',ROOT/'scripts/rook/render_regions.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr);validate=rr.validate
source=ROOT/'build/rook-mission/035-rim-strength/rook.blend';out=ROOT/'build/rook-mission/037-rim-bevel-only';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
ob=next(o for o in s.objects if o.get('rook_render_receiver')=='rim');m=ob.data
co=np.array([v.co[:] for v in m.vertices],np.float32);lv=np.array([v.vertex_index for v in m.loops]);starts=np.array([p.loop_start for p in m.polygons]);counts=np.array([p.loop_total for p in m.polygons]);normals=np.array([n.vector[:] for n in m.corner_normals],np.float32);uvs={u.name:np.array([v.uv[:] for v in u.data],np.float32) for u in m.uv_layers}
select=np.array([p.center.z>2.68 and .65<p.normal.z<.98 for p in m.polygons]);materials=list(m.materials)
newparts=[]
for selection,name in [(~select,'rim'),(select,'rim_bevel')]:
 ids=np.flatnonzero(selection);loops=np.concatenate([np.arange(starts[i],starts[i]+counts[i]) for i in ids]);verts,inv=np.unique(lv[loops],return_inverse=True);faces=[a.tolist() for a in np.split(inv,np.cumsum(counts[ids])[:-1])]
 me=bpy.data.meshes.new('Rook receiver '+name);me.from_pydata(co[verts].tolist(),[],faces);me.update()
 for i,p in enumerate(me.polygons):p.use_smooth=m.polygons[int(ids[i])].use_smooth
 for key,uv in uvs.items():me.uv_layers.new(name=key).data.foreach_set('uv',uv[loops].reshape(-1))
 me.normals_split_custom_set(normals[loops].tolist())
 for mat in materials:me.materials.append(mat)
 new=bpy.data.objects.new(me.name,me);s.collection.objects.link(new);new.matrix_world=ob.matrix_world.copy();new['rook_render_receiver']=name;newparts.append(new)
for c in list(bpy.data.collections):
 if ob.name in c.objects and c!=s.collection:
  for new in newparts:
   if new.name not in c.objects:c.objects.link(new)
bpy.data.objects.remove(ob,do_unlink=True)
receiver=bpy.data.collections.new('Measured upper bevel only');receiver.objects.link(newparts[1])
for light in s.objects:
 if light.type=='LIGHT' and light.name.startswith('Measured rim '):light.light_linking.receiver_collection=receiver
report=validate(s)
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);report=validate(s);bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'selection':'face center z>2.68 and 0.65<geometric normal z<0.98','bevel_faces':int(select.sum()),'receiver_validation':report},indent=2)+'\n')
print('BEVEL_ONLY_DONE')
