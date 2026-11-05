"""Bake diffuse pigment only; restore BSDF, reopen, and render the saved model."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/a.source),load_ui=False)
s=bpy.context.scene;objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
mat=objects[0].data.materials[0];assert all(o.data.materials[0]==mat for o in objects)
n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];out=n['Material Output'];pigment=bs.inputs['Base Color'].links[0].from_socket
source_pixels={}
for image in bpy.data.images:
    if image.type not in {'RENDER_RESULT','COMPOSITING'} and image.size[0] and image.size[1]:
        values=np.array(image.pixels[:],dtype=np.float32)
        source_pixels[image.name]=hashlib.sha256(values.tobytes()).hexdigest()
emission=n.new('ShaderNodeEmission');l.new(pigment,emission.inputs['Color']);l.new(emission.outputs[0],out.inputs['Surface'])
atlas=bpy.data.images.new('Bishop boxwood albedo — no illumination',width=2048,height=2048,alpha=False);atlas.colorspace_settings.name='sRGB'
previous_target=n.get('Baked boxwood pigment')
if previous_target:previous_target.name='Previous baked boxwood pigment'
target=n.new('ShaderNodeTexImage');target.name='Baked boxwood pigment';target.image=atlas
for node in n:node.select=False
target.select=True;n.active=target
# Boolean cut materials retain an old atlas node from their source material.
# Blender bakes every material's active image, not just the selected main node.
# Give cuts their own disposable target so no input pigment can be overwritten.
scratch=bpy.data.images.new('Disposable cut bake target',width=256,height=256,alpha=False)
for cut in {m for ob in objects for m in ob.data.materials if m and m!=mat}:
    cut_nodes=cut.node_tree.nodes
    for node in cut_nodes:node.select=False
    cut_target=cut_nodes.new('ShaderNodeTexImage');cut_target.image=scratch
    cut_target.select=True;cut_nodes.active=cut_target
for o in s.objects:o.select_set(False)
for o in objects:o.select_set(True);o.data.uv_layers.active=o.data.uv_layers['Wood atlas'];o.data.uv_layers['Wood atlas'].active_render=True
bpy.context.view_layer.objects.active=objects[0]
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.cycles.samples=1;s.render.bake.margin=12
bpy.ops.object.bake(type='EMIT',use_clear=True)
for name,before in source_pixels.items():
    image=bpy.data.images[name];after=hashlib.sha256(np.array(image.pixels[:],dtype=np.float32).tobytes()).hexdigest()
    assert after==before, 'Bake modified an input image: '+name
texture=ROOT/'assets/bishop/bishop-boxwood-albedo.png';atlas.filepath_raw=str(texture);atlas.file_format='PNG';atlas.save();atlas.pack()
l.new(bs.outputs['BSDF'],out.inputs['Surface']);n.remove(emission)
uv=n.new('ShaderNodeUVMap');uv.uv_map='Wood atlas';l.new(uv.outputs['UV'],target.inputs['Vector']);l.new(target.outputs['Color'],bs.inputs['Base Color'])
sys.path.insert(0,str(Path(__file__).parent))
from cut_material import assign_cut_material
assign_cut_material(s)
# The measurement images are intermediate pigment tools. Keep only nodes that
# actually feed the final BSDFs, so the editable saved model remains portable.
for material in {m for obj in objects for m in obj.data.materials if m and m.use_nodes}:
    nodes=material.node_tree.nodes;reachable=set()
    def visit(node):
        if node in reachable:return
        reachable.add(node)
        for socket in node.inputs:
            for link in socket.links:visit(link.from_node)
    for node in nodes:
        if node.type=='OUTPUT_MATERIAL':visit(node)
    for node in list(nodes):
        if node not in reachable:nodes.remove(node)
for material in list(bpy.data.materials):
    if material.users==0:bpy.data.materials.remove(material)
for image in list(bpy.data.images):
    if image.users==0:bpy.data.images.remove(image)
# The relief retains its separate inference graph; albedo baking never captures light.
s['bishop_albedo_texture']='assets/bishop/bishop-boxwood-albedo.png';s['bishop_albedo_sha256']=hashlib.sha256(texture.read_bytes()).hexdigest();s['bishop_albedo_bakes_lighting']=False
s.cycles.samples=96;s.render.resolution_percentage=100
dest=ROOT/a.out;dest.mkdir(parents=True,exist_ok=True);s.render.filepath=str(dest/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'bishop.blend'))
# Reopen instead of trusting in-memory packed pixels.
bpy.ops.wm.open_mainfile(filepath=str(dest/'bishop.blend'),load_ui=False)
s=bpy.context.scene;mat=next(o for o in s.objects if o.type=='MESH' and not o.hide_render).data.materials[0]
assert mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED'
packed=mat.node_tree.nodes['Baked boxwood pigment'].image;assert packed.packed_file
disk=bpy.data.images.load(str(texture),check_existing=False)
aa=np.array(packed.pixels[:]);bb=np.array(disk.pixels[:]);err=float(np.max(np.abs(aa-bb)));assert err<1e-6,err
assert len([o for o in s.objects if o.type=='MESH' and not o.hide_render])==2
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU';bpy.ops.render.render(write_still=True)
(dest/'bake-validation.json').write_text(json.dumps({'pigment_only':True,'input_image_pixels_preserved':True,'checked_input_images':source_pixels,'reopened_packed_pixel_max_error':err,'texture_sha256':s['bishop_albedo_sha256'],'render_shader':'Principled BSDF','source_sha256':hashlib.sha256((ROOT/a.source).read_bytes()).hexdigest(),'saved_model_sha256':hashlib.sha256((dest/'bishop.blend').read_bytes()).hexdigest()},indent=2)+'\n')
print('BISHOP_PIGMENT_BAKE_REOPEN_VALIDATED',flush=True)
