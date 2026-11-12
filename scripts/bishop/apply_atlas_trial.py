"""Render an isolated bishop atlas trial with unchanged geometry, camera and lights."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from bishop_scene import editable_meshes
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--atlas',required=True);p.add_argument('--variant',required=True);p.add_argument('--samples',type=int,default=48)
p.add_argument('--bump-strength',type=float,help='Diagnostic relief isolation, recorded explicitly.')
p.add_argument('--no-render',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;atlas=ROOT/a.atlas
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
mat=editable_meshes(s)[0].data.materials[0]
image=bpy.data.images.load(str(atlas),check_existing=False);image.pack();mat.node_tree.nodes['Baked boxwood pigment'].image=image
assert mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED'
if a.bump_strength is not None:
    for material in {m for o in s.objects if o.type=='MESH' and not o.hide_render for m in o.data.materials if m and m.use_nodes}:
        for node in material.node_tree.nodes:
            if node.type=='BUMP':node.inputs['Strength'].default_value=a.bump_strength
record={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'atlas':a.atlas,'atlas_sha256':hashlib.sha256(atlas.read_bytes()).hexdigest(),'variant':a.variant,'geometry_camera_lights_unchanged':True}
record['diagnostic_bump_strength']=a.bump_strength
s['bishop_hidden_pigment_trial']=json.dumps(record,sort_keys=True);s['bishop_albedo_sha256']=record['atlas_sha256'];s['bishop_albedo_texture']=a.atlas
out=ROOT/'build/bishop-mission'/a.variant;out.mkdir(parents=True,exist_ok=True)
s.cycles.samples=a.samples;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
mat=editable_meshes(s)[0].data.materials[0]
packed=mat.node_tree.nodes['Baked boxwood pigment'].image;assert packed.packed_file
disk=bpy.data.images.load(str(atlas),check_existing=False)
pixel_error=float(np.max(np.abs(np.array(packed.pixels[:],dtype=np.float32)-np.array(disk.pixels[:],dtype=np.float32))))
assert pixel_error==0,pixel_error
bpy.data.images.remove(disk)
record['reopened_before_render']=True;record['packed_pixel_max_error']=pixel_error
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
if not a.no_render:bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256']
record['saved_model_sha256']=hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest()
(out/'trial-validation.json').write_text(json.dumps(record,indent=2)+'\n');print('BISHOP_ATLAS_TRIAL_COMPLETE',json.dumps(record),flush=True)
