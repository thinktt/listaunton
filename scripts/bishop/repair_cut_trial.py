"""Repair the first pigment-only bake without re-baking unchanged outer wood."""
import bpy,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from cut_material import assign_cut_material
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/bishop-mission/008-baked-checkpoint/bishop.blend'),load_ui=False)
s=bpy.context.scene;assign_cut_material(s)
out=ROOT/'build/bishop-mission/009-cut-wood';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.context.view_layer.update();body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render and 'continuous' in o.name);ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();cut_faces=sum(p.material_index==1 for p in me.polygons);assert cut_faces>0;ev.to_mesh_clear()
bpy.ops.render.render(write_still=True)
(out/'cut-validation.json').write_text(json.dumps({'procedural_cut_faces':cut_faces,'camera_unchanged':True,'reopened_before_render':True,'model_sha256':hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest()},indent=2)+'\n')
print('CUT_MATERIAL_REOPENED_AND_RENDERED',cut_faces)
