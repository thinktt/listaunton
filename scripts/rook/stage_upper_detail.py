"""Stage accepted foot-light candidate without overwriting public assets."""
from pathlib import Path
import bpy,sys,json,hashlib,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
sys.path.insert(0,str(ROOT/'scripts/rook'));import importlib.util
spec=importlib.util.spec_from_file_location('rook_regions',ROOT/'scripts/rook/render_regions.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr);validate=rr.validate;closed_body=rr.closed_body
stage=Path(sys.argv[sys.argv.index('--')+1]);source=ROOT/'build/rook-mission/063-local-pigment/rook.blend';out=stage/'assets/rook';out.mkdir(parents=True,exist_ok=True);model=stage/'models/rook/rook-rebuilt.blend';model.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;validate(s);closed_body(s).hide_set(True);gpu(s)
s['reconstruction']='Rook checkpoint 063: local upper-body pigment detail repair; geometry and lighting retained. Assumed 54-degree camera; finish incomplete.'
s['rook_pigment_image']=closed_body(s).data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image.name;s['rook_pigment_atlas']='assets/rook/pigment.png';s.render.filepath=str(out/'render.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(model));bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;gpu(s);validate(s);bpy.ops.render.render(write_still=True)
c=s.camera;c.data.shift_x=0;c.data.shift_y=0;c.data.sensor_fit='VERTICAL';c.data.ortho_scale=4.3;c.location=(0,-12,1.4);c.rotation_euler=(Vector((0,0,1.4))-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'profile.png');bpy.ops.render.render(write_still=True)
c.location=(0,12,1.4);c.rotation_euler=(Vector((0,0,1.4))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'rear.png');bpy.ops.render.render(write_still=True)
(out/'checkpoint.json').write_text(json.dumps({'checkpoint':63,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source_trial_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'change':'Upper patch reference-informed pigment repair; all geometry, UVs and lights preserved','unfinished':['turret and shoulder reflections','baked lighting contamination','side neck pigment transitions','inferred hidden form']},indent=2)+'\n');print('FOOT_CHECKPOINT_STAGED')

# Unsaved neutral diagnostic from the delivered fixed camera.
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;gpu(s)
clay=bpy.data.materials.new('Neutral floor diagnostic');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.35
for ob in s.objects:
    if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(clay)
    if ob.type=='LIGHT' and ob.name.startswith(('Rook ','Measured ')):ob.data.energy=0
s.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)


