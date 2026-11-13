from pathlib import Path
import bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='77221a063a8dbdd5f01545312c98e5bf31d4f86f3d6cbe0ea169ff198060a33e'
for num in [57,58]:
 out=ROOT/f'build/rook-mission/{num:03d}-local-pigment';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;body=next(o for o in s.objects if o.get('rook_editable_control'));bs=body.data.materials[0].node_tree.nodes['Principled BSDF'];tex=bs.inputs['Base Color'].links[0].from_node;assert tex.type=='TEX_IMAGE';image=bpy.data.images.load(str(out/'pigment.png'),check_existing=False);image.colorspace_settings.name='sRGB';image.pack();tex.image=image;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));p=json.loads((out/'parameters.json').read_text());p.update(source_model_sha256=sha(source),model_sha256=sha(out/'rook.blend'));(out/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')

