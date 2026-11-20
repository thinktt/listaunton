"""Attach inferred pigment to the real mesh; preserve its BSDF and scene lights."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--directory',required=True);p.add_argument('--variant',default='034-inferred-pigment');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;directory=ROOT/args.directory;record=json.loads((directory/'manifest.json').read_text());assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
for mod in obj.modifiers:
 if mod.type=='SUBSURF':mod.levels=mod.render_levels
bpy.context.view_layer.update();tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get());view=scene.camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
uvs=[];weights=[]
for v in obj.data.vertices:
 co=obj.matrix_world@v.co;point=world_to_camera_view(scene,scene.camera,co);uvs.append((point.x,point.y))
 loc,_,_,_=tree.ray_cast(co+view*10,-view,20)
 facing=max(0,min(1,(v.normal.dot(view)-.08)/.4));weights.append(facing if loc is not None and abs((loc-co).dot(view))<.06 else 0)
uv=obj.data.uv_layers.get('Inferred pigment projection') or obj.data.uv_layers.new(name='Inferred pigment projection')
for loop in obj.data.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
attr=obj.data.attributes.get('Inferred pigment coverage') or obj.data.attributes.new(name='Inferred pigment coverage',type='FLOAT',domain='POINT');attr.data.foreach_set('value',weights)
rgba=np.load(directory/'inferred-pigment.npy');assert np.isfinite(rgba).all();h,w=rgba.shape[:2]
im=bpy.data.images.new('Queen inferred diffuse pigment',width=w,height=h,alpha=True,float_buffer=True);im.colorspace_settings.name='Linear Rec.709';im.alpha_mode='STRAIGHT';im.pixels.foreach_set(rgba[::-1].copy().reshape(-1));im.file_format='OPEN_EXR';im.filepath_raw=str(directory/'inferred-pigment.exr');im.save();im.pack()
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket
tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;links.new(uvnode.outputs[0],tex.inputs['Vector'])
coverage=nodes.new('ShaderNodeAttribute');coverage.attribute_name=attr.name;weight=nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';links.new(coverage.outputs['Fac'],weight.inputs[0]);links.new(tex.outputs['Alpha'],weight.inputs[1])
mix=nodes.new('ShaderNodeMixRGB');links.new(weight.outputs[0],mix.inputs[0]);links.new(old,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');assert output.inputs['Surface'].links[0].from_node==bs
cfg=json.loads(scene['mission_material_config']);cfg.update({'variant':args.variant,'inferred_pigment':{'source':args.source,'response_directory':args.directory,'projection_uv':uv.name,'coverage_attribute':attr.name,'image':str(im.filepath_raw),'highlight_confidence':True,'inference':json.loads((directory/'inference.json').read_text())}});scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(out/'wood.png');scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('INFERRED_PIGMENT_DONE',flush=True)
