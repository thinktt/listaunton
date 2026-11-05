"""Bake a local pigment patch and coverage into existing UVs without changing a model."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;obj=editable_mesh(scene)
out=ROOT/a.out;out.mkdir(exist_ok=True,parents=True)
for o in scene.objects:
    if o.get('mission_render_region'):o.hide_render=True
obj.hide_render=False;obj.hide_set(False)
uv=obj.data.uv_layers['Pigment atlas'];obj.data.uv_layers.active=uv;uv.active_render=True
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');color=bs.inputs['Base Color'].links[0].from_socket
mix=color.node;assert mix.type=='MIX_RGB' and mix.inputs[0].is_linked
mask=mix.inputs[0].links[0].from_socket
output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
em=nodes.new('ShaderNodeEmission');links.new(em.outputs[0],output.inputs['Surface'])
target=nodes.new('ShaderNodeTexImage')
for n in nodes:n.select=False
target.select=True;nodes.active=target
for selected in bpy.context.selected_objects:selected.select_set(False)
obj.select_set(True);bpy.context.view_layer.objects.active=obj
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
scene.cycles.samples=1;scene.render.bake.margin=8
records={}
for name,socket,space in [('color',color,'sRGB'),('coverage',mask,'Non-Color')]:
    links.new(socket,em.inputs['Color'])
    atlas=bpy.data.images.new('Local pigment '+name,width=2048,height=2048,alpha=False)
    atlas.colorspace_settings.name=space;target.image=atlas
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    path=out/(name+'.png');atlas.filepath_raw=str(path);atlas.file_format='PNG';atlas.save()
    records[name]={'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'colorspace':space}
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'bake.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,'uv':'Pigment atlas','size':2048,'samples':1,'margin':8,'emission_only':True,'bakes_lighting':False,'files':records},indent=2)+'\n')
print('PIGMENT_PATCH_BAKED',flush=True)
