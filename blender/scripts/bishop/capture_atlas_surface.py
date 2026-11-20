"""Measure atlas positions/normals and fixed-view visibility; never save the scene."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from bishop_scene import editable_meshes
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out
out.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
objects=editable_meshes(s)
for ob in s.objects:
    if ob.get('bishop_render_region'):ob.hide_render=True
for ob in objects:ob.hide_render=False
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();points=[]
for ob in objects:
    ev=ob.evaluated_get(graph);me=ev.to_mesh();points.extend(tuple(ob.matrix_world@v.co) for v in me.vertices);ev.to_mesh_clear()
points=np.array(points);lo=points.min(0)-.1;extent=points.max(0)+.1-lo
mat=bpy.data.materials.new('Atlas surface measurement only');mat.use_nodes=True
ns=mat.node_tree.nodes;ls=mat.node_tree.links;ns.clear()
geom=ns.new('ShaderNodeNewGeometry');emission=ns.new('ShaderNodeEmission');output=ns.new('ShaderNodeOutputMaterial')
ls.new(emission.outputs[0],output.inputs['Surface'])
def vector_math(operation,source,value):
    n=ns.new('ShaderNodeVectorMath');n.operation=operation;ls.new(source,n.inputs[0]);n.inputs[1].default_value=tuple(value)
    return n.outputs['Vector']
position=vector_math('SUBTRACT',geom.outputs['Position'],lo)
position=vector_math('DIVIDE',position,extent)
position=vector_math('MULTIPLY',position,[.8]*3)
position=vector_math('ADD',position,[.1]*3)
normal=vector_math('MULTIPLY',geom.outputs['Normal'],[.5]*3)
normal=vector_math('ADD',normal,[.5]*3)
coverage=ns.new('ShaderNodeAttribute');coverage.attribute_name='Pigment coverage'
target=ns.new('ShaderNodeTexImage');target.name='Disposable measurement target'
for ob in s.objects:ob.select_set(False)
for ob in objects:
    ob.data.materials.clear();ob.data.materials.append(mat)
    ob.data.uv_layers.active=ob.data.uv_layers['Wood atlas'];ob.data.uv_layers['Wood atlas'].active_render=True
    ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
s.cycles.samples=1;s.render.bake.margin=0
for name,socket in [('position',position),('normal',normal),('legacy-coverage',coverage.outputs['Fac'])]:
    im=bpy.data.images.new('Measured '+name,width=2048,height=2048,alpha=True,float_buffer=True)
    im.colorspace_settings.name='Non-Color';target.image=im;ns.active=target
    for n in ns:n.select=False
    target.select=True;ls.new(socket,emission.inputs['Color'])
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    values=np.array(im.pixels[:],dtype=np.float32).reshape(2048,2048,4)[::-1].copy()
    np.save(out/(name+'.npy'),values)
    print('ATLAS_FIELD_BAKED',name,flush=True)
ls.new(position,emission.inputs['Color'])
s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=False
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.render.filepath=str(out/'fixed-position.exr');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(out/'fixed-position.exr'),check_existing=False)
np.save(out/'fixed-position.npy',np.array(im.pixels[:],dtype=np.float32).reshape(s.render.resolution_y,s.render.resolution_x,4)[::-1].copy())
graph=bpy.context.evaluated_depsgraph_get();cam=s.camera
matrix=cam.calc_matrix_camera(graph,x=s.render.resolution_x,y=s.render.resolution_y)@cam.matrix_world.inverted()
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'encode_min':lo.tolist(),'encode_extent':extent.tolist(),'encode_scale':.8,'encode_offset':.1,
 'world_to_clip':[list(row) for row in matrix],
 'view_direction':list(cam.matrix_world.to_3x3()@__import__('mathutils').Vector((0,0,1))),
 'image_size':[s.render.resolution_x,s.render.resolution_y],'atlas_size':[2048,2048],
 'note':'Unsaved emission measurements of actual evaluated surfaces; diagnostic only, not beauty renders.'},indent=2)+'\n')
print('ATLAS_SURFACE_CAPTURE_COMPLETE',flush=True)
