"""Test an extended reflected strip on the accepted rook, without receiver masks."""
from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'models/rook/rook-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9eaaaaadfd2195591508cda798d56c27aa263ee3baa9424ded8acf76d6e4349c'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
for ob in s.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Rook '):ob.data.energy=0
for label,z,energy in [('010-high-strip',5,450),('011-low-strip',2.5,300)]:
    for ob in list(s.objects):
        if ob.name.startswith('Rook strip'):bpy.data.objects.remove(ob,do_unlink=True)
    d=bpy.data.lights.new('Rook strip','AREA');d.shape='RECTANGLE';d.size=8;d.size_y=.12;d.energy=energy;d.color=(1,1,1)
    ob=bpy.data.objects.new(d.name,d);s.collection.objects.link(ob);ob.location=(0,-4,z);ob.rotation_euler=(Vector((0,0,1.3))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_diffuse=False;ob.visible_glossy=True
    out=ROOT/'build/rook-mission'/label;out.mkdir(parents=True,exist_ok=True);s.cycles.samples=64;s.render.resolution_percentage=100;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'light_position':[0,-4,z],'width':8,'height':.12,'energy':energy,'material_unchanged':True,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()},indent=2)+'\n');print('STRIP_DONE',label,flush=True)
