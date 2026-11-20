"""Build the next editable model from the accepted native and the two graded wood studies."""
from pathlib import Path
import json,sys,hashlib
import bpy
root,source,packet,out=map(lambda s:Path(s).resolve(),sys.argv[-4:])
sys.path[:0]=[str(packet),str(root/'scripts/knight')]
from apply import apply
from mission_scene import sha,save_model,configure_render,use_side_camera,visible_meshes,render,json_file
from project_mission_pigment import visible_meshes
from export_mission import export
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
pigment=json.loads((out/'pigment.json').read_bytes())
if sha(source)!='61b80aa4cf9ab766ca554f33fb79137bad678dcb921d9ff86e16feaf6c36841b':raise ValueError('Unexpected accepted parent')
apply(scene,packet)
tex=out/'pigment.png'
mat=visible_meshes(scene)[0].data.materials[0]
node=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
old=node.image
assert hashlib.sha256(bytes(old.packed_file.data)).hexdigest()==pigment['parent']
assert sha(tex)==pigment['texture']
raw=tex.read_bytes()
image=bpy.data.images.load(str(tex),check_existing=False)
image.name='Knight | chest and turned walnut'
image.colorspace_settings.name='sRGB'
image.pack(data=raw,data_len=len(raw))
node.image=image
if old.users==0:bpy.data.images.remove(old)
configure_render(scene,144);save_model(scene,out/'knight.blend')
bpy.ops.wm.open_mainfile(filepath=str(out/'knight.blend'),load_ui=False)
scene=bpy.context.scene;configure_render(scene,144)
export(scene,tex,output=out,source=out/'knight.blend')
render(scene,out/'wood.png')
use_side_camera(scene);render(scene,out/'wood-side.png')
json_file(out/'combination.json',{'parent':sha(source),'model':sha(out/'knight.blend'),'fixed':sha(out/'wood.png'),'profile':sha(out/'wood-side.png'),'pigment':pigment,'chest_recipe':sha(packet/'recipe.json')})
