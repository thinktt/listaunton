"""Read-only fixed clay, profile and optional fresh beauty from a saved king."""
from pathlib import Path
import argparse,hashlib,sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls,assign_material
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--beauty-only',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
if a.beauty_only:
    s.render.filepath=str(out/'wood-reopened.png');bpy.ops.render.render(write_still=True)
else:
    objects=controls(s);old=[o.data.materials[0] for o in objects]
    clay=bpy.data.materials.new('King saved-file inspection clay');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
    for ob in objects:assign_material(s,ob,clay)
    s.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
    for ob,mat in zip(objects,old):assign_material(s,ob,mat)
    cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6
    cam.location=(0,-16,2.65);cam.rotation_euler=(Vector((0,0,2.65))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'profile.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('KING_SAVED_DIAGNOSTICS_PASS')
