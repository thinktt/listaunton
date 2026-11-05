"""Read-only reopened beauty and orthographic side/rear inspections."""
from pathlib import Path
import argparse,hashlib,sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True);before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);s.render.filepath=str(out/'wood-reopened.png');bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6
s.render.resolution_x=600;s.render.resolution_y=900
for name,pos in [('rear',(0,16,2.65)),('side',(16,0,2.65))]:
    cam.location=pos;cam.rotation_euler=(Vector((0,0,2.65))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('KING_INSPECTION_DONE')
