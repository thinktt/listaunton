from pathlib import Path
import sys,json,hashlib
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/019-normal-strips/rook.blend'
out=ROOT/'build/rook-mission/020-linked-strips';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
co=np.array([v.co[:] for v in m.vertices],np.float32)
lv=np.array([l.vertex_index for l in m.loops]);starts=np.array([p.loop_start for p in m.polygons]);counts=np.array([p.loop_total for p in m.polygons])
centers=np.add.reduceat(co[lv],starts,axis=0)/counts[:,None];z=centers[:,2];r=np.linalg.norm(centers[:,:2],axis=1)
labels=np.zeros(len(counts),int)
labels[((z>2.68)&(r>.50))|((z>2.53)&(z<2.58)&(r>.58))]=1
labels[(z>.65)&(z<.74)&(r>.60)]=2
labels[(z>.18)&(z<.24)&(r>.84)]=3
normals=np.array([n.vector[:] for n in m.corner_normals],np.float32)
uvs={u.name:np.array([v.uv[:] for v in u.data],np.float32) for u in m.uv_layers}
parts={};report=[]
for label,name in enumerate(['body','rim','shoulder','foot']):
    ids=np.flatnonzero(labels==label);loops=np.concatenate([np.arange(starts[i],starts[i]+counts[i]) for i in ids]);verts,inv=np.unique(lv[loops],return_inverse=True)
    faces=[x.tolist() for x in np.split(inv,np.cumsum(counts[ids])[:-1])]
    mesh=bpy.data.meshes.new('Rook receiver '+name);mesh.from_pydata(co[verts].tolist(),[],faces);mesh.update()
    for i,p in enumerate(mesh.polygons):p.use_smooth=m.polygons[int(ids[i])].use_smooth
    for un,uv in uvs.items():mesh.uv_layers.new(name=un).data.foreach_set('uv',uv[loops].reshape(-1))
    mesh.normals_split_custom_set(normals[loops].tolist())
    for mat in body.data.materials:mesh.materials.append(mat)
    ob=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(ob);ob.matrix_world=body.matrix_world.copy();ob['rook_render_receiver']=name;parts[name]=ob
    check=np.array([v.co[:] for v in mesh.vertices],np.float32)
    assert np.array_equal(check,co[verts])
    for un,uv in uvs.items():assert np.array_equal(np.array([v.uv[:] for v in mesh.uv_layers[un].data],np.float32),uv[loops])
    actual=np.array([n.vector[:] for n in mesh.corner_normals]);err=float(np.abs(actual-normals[loops]).max());assert err<1e-3,err # Diagnostic only: encoded normals are measured, not claimed exact
    report.append({'region':name,'faces':len(ids),'normal_max_error':err,'coordinates_uv_exact':True})
assert sum(v['faces'] for v in report)==len(m.polygons)
e.to_mesh_clear();body.hide_render=True;body['rook_editable_control']=True
for region in ['rim','shoulder','foot']:
    collection=bpy.data.collections.new('Rook receivers '+region);collection.objects.link(parts[region])
    for light in s.objects:
        if light.type=='LIGHT' and light.name.startswith('Rook normal strip '):
            light.data.energy=40;name=light.name.split()[-1];group='shoulder' if name.startswith('shoulder') else 'foot' if name.startswith('foot') else 'rim'
            if group==region:light.light_linking.receiver_collection=collection
s.cycles.samples=64;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
(out/'receiver-validation.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'regions':report,'all_faces_partitioned_once':True,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()},indent=2)+'\n')
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
print('ROOK_EDGE_RECEIVERS_DONE')
