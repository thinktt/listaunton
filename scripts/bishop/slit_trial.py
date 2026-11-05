"""Round only the bishop saw-cut termination in an isolated, reversible trial."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('config',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads(args.config.read_text());source=ROOT/cfg['source']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256']
out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
body=bpy.data.objects['Bishop - continuous turned body']
modifier=next(m for m in body.modifiers if m.type=='BOOLEAN')
cutter=modifier.object

def state():
    meshes={}
    for ob in scene.objects:
        if ob.type!='MESH':continue
        payload={'vertices':[list(v.co) for v in ob.data.vertices],
                 'faces':[list(f.vertices) for f in ob.data.polygons],
                 'matrix':[list(row) for row in ob.matrix_world],
                 'uvs':[[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers]}
        meshes[ob.name]=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    camera={'matrix':[list(row) for row in scene.camera.matrix_world],
            'scale':scene.camera.data.ortho_scale,'shift_x':scene.camera.data.shift_x,
            'shift_y':scene.camera.data.shift_y}
    lights={ob.name:{'matrix':[list(row) for row in ob.matrix_world],
                    'power':ob.data.energy,'color':list(ob.data.color),
                    'size':ob.data.size,'size_y':ob.data.size_y,'spread':ob.data.spread,
                    'diffuse':ob.visible_diffuse,'glossy':ob.visible_glossy}
            for ob in scene.objects if ob.type=='LIGHT'}
    return {'mesh_control_and_uv_hashes':meshes,'camera':camera,'lights':lights}

before=state()
old=np.array([list(v.co) for v in cutter.data.vertices])
lo=old.min(0);hi=old.max(0);halfwidth=(hi[0]-lo[0])/2;center=(hi[0]+lo[0])/2
depth=halfwidth*cfg['depth_factor'];segments=cfg.get('segments',32)
# Same parallel sides and full front-to-back opening, with a rounded floor.
cross=[(lo[0],hi[2])]
cross += [(center+halfwidth*math.cos(math.pi-i*math.pi/segments),
           lo[2]-depth*math.sin(math.pi-i*math.pi/segments)) for i in range(segments+1)]
cross += [(hi[0],hi[2])]
count=len(cross)
vertices=[(x,y,z) for y in [lo[1],hi[1]] for x,z in cross]
faces=[tuple(range(count)),tuple(reversed(range(count,2*count)))]
faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
mesh=bpy.data.meshes.new('Mitre slot with rounded floor')
mesh.from_pydata(vertices,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
for material in cutter.data.materials:mesh.materials.append(material)
for face in mesh.polygons:face.material_index=1
cutter.data=mesh
bevel=next(m for m in body.modifiers if m.type=='BEVEL')
bevel_before=bevel.width;bevel.width*=cfg.get('bevel_factor',1)
bpy.context.view_layer.update()
after=state()
assert before['camera']==after['camera'] and before['lights']==after['lights']
changed=[name for name in before['mesh_control_and_uv_hashes'] if before['mesh_control_and_uv_hashes'][name]!=after['mesh_control_and_uv_hashes'][name]]
assert changed==[cutter.name],changed
scene['bishop_slit_trial']=json.dumps(cfg,sort_keys=True)
scene.cycles.samples=cfg.get('samples',48);scene.render.resolution_percentage=100
scene.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False)
scene=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
report={'config':cfg,'source_sha256':sha(source),'model_sha256':sha(out/'bishop.blend'),
        'render_sha256':sha(out/'wood.png'),'only_changed_control_object':changed,
        'camera_unchanged':before['camera']==after['camera'],'lighting_unchanged':before['lights']==after['lights'],
        'original_cutter_local_bounds':[lo.tolist(),hi.tolist()],'floor_extension':float(depth),
        'new_cutter_vertices':vertices,'new_cutter_faces':faces,
        'bevel_width_before':bevel_before,'bevel_width_after':bevel_before*cfg.get('bevel_factor',1),
        'preserved_state':before,'new_state':after,'saved_and_reopened':True}
(out/'parameters.json').write_text(json.dumps(report,indent=2)+'\n')
print('SLIT_TRIAL_COMPLETE',cfg['variant'],flush=True)
