"""Apply a de-lit reference texture to visible surface, with continuous wood elsewhere.

The texture sticks to the mesh through a stored UV layer; no camera-facing
billboard, emission beauty render, or view-dependent reference substitution.
"""
from pathlib import Path
import json
import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/011-directional-wood/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
graph=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(obj,graph)
view=scene.camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
uvs=[];weights=[]
for v in obj.data.vertices:
    co=obj.matrix_world@v.co;p=world_to_camera_view(scene,scene.camera,co)
    uvs.append((p.x,p.y))
    facing=max(0,min(1,(v.normal.dot(view)-.08)/.4))
    loc,_,_,_=tree.ray_cast(co+view*10,-view,20)
    visible=loc is not None and abs((loc-co).dot(view))<.06
    weights.append(facing if visible else 0)
uv=obj.data.uv_layers.get('Reference paint') or obj.data.uv_layers.new(name='Reference paint')
for loop in obj.data.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
attr=obj.data.attributes.get('Reference coverage') or obj.data.attributes.new(name='Reference coverage',type='FLOAT',domain='POINT')
attr.data.foreach_set('value',weights)
mat=obj.data.materials[0];mat.name='Walnut - reference-derived pigment';nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket
image=bpy.data.images.load(str(ROOT/'assets/queen/reference-delit-source.png'),check_existing=False);image.pack()
tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';tex.label='Derived unlit reference, original unchanged'
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
coverage=nodes.new('ShaderNodeAttribute');coverage.attribute_name=attr.name
gray=nodes.new('ShaderNodeRGBToBW');links.new(tex.outputs['Color'],gray.inputs[0])
edge=nodes.new('ShaderNodeMapRange');edge.inputs['From Min'].default_value=.004;edge.inputs['From Max'].default_value=.02
links.new(gray.outputs[0],edge.inputs['Value'])
weight=nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';links.new(coverage.outputs['Fac'],weight.inputs[0]);links.new(edge.outputs[0],weight.inputs[1])
strength=nodes.new('ShaderNodeMath');strength.operation='MULTIPLY';strength.inputs[1].default_value=.9;links.new(weight.outputs[0],strength.inputs[0])
grade=nodes.new('ShaderNodeHueSaturation');grade.inputs['Value'].default_value=.55;links.new(tex.outputs['Color'],grade.inputs['Color'])
mix=nodes.new('ShaderNodeMixRGB');links.new(strength.outputs[0],mix.inputs[0]);links.new(old,mix.inputs[1]);links.new(grade.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
out=ROOT/'build/queen-mission/012-projected-pigment';out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
scene['mission_variant']='012-projected-pigment';scene['projection_texture']='assets/queen/reference-delit-source.png'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'derived_texture':'assets/queen/reference-delit-source.png','projection_weight':.9,'projection_value':.55,'visibility_tolerance':.06,'coverage_min_max':[min(weights),max(weights)],'nonzero_control_weights':sum(w>0 for w in weights),'real_lighting':True},indent=2))
print('PROJECTED_MATERIAL_DONE',flush=True)
