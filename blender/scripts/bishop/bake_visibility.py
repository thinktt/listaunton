"""Bake a conservative fixed-camera visibility mask; source model/images stay untouched."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--tolerance',type=float,default=.12)
p.add_argument('--facing-start',type=float);p.add_argument('--facing-full',type=float,default=.5)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render];graph=bpy.context.evaluated_depsgraph_get()
view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized();trees=[]
for ob in objects:
    ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles()
    vertices=[ob.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
    trees.append(BVHTree.FromPolygons(vertices,tris,all_triangles=True));ev.to_mesh_clear()
stats={}
for ob in objects:
    values=[]
    for vertex in ob.data.vertices:
        co=ob.matrix_world@vertex.co;distance=100
        for tree in trees:
            hit=tree.ray_cast(co+view*12,-view,24)
            if hit[0] is not None:distance=min(distance,hit[3])
        values.append(1.0 if abs(distance-12)<a.tolerance else 0.0)
    attr=ob.data.attributes.new(name='Bishop protected reference visibility',type='FLOAT',domain='POINT')
    attr.data.foreach_set('value',values);stats[ob.name]={'protected_vertices':sum(values),'total_vertices':len(values)}
    ob.data.uv_layers.active=ob.data.uv_layers['Wood atlas'];ob.data.uv_layers['Wood atlas'].active_render=True
main=objects[0].data.materials[0];nodes=main.node_tree.nodes;links=main.node_tree.links
field=nodes.new('ShaderNodeAttribute');field.attribute_name='Bishop protected reference visibility'
em=nodes.new('ShaderNodeEmission');links.new(field.outputs['Fac'],em.inputs['Color']);links.new(em.outputs[0],nodes['Material Output'].inputs['Surface'])
if a.facing_start is not None:
    assert -1<=a.facing_start<a.facing_full<=1
    geometry=nodes.new('ShaderNodeNewGeometry');dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    links.new(geometry.outputs['Normal'],dot.inputs[0]);dot.inputs[1].default_value=view
    mapping=nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=a.facing_start;mapping.inputs['From Max'].default_value=a.facing_full;mapping.clamp=True
    links.new(dot.outputs['Value'],mapping.inputs['Value'])
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';links.new(field.outputs['Fac'],multiply.inputs[0]);links.new(mapping.outputs['Result'],multiply.inputs[1]);links.new(multiply.outputs[0],em.inputs['Color'])
image=bpy.data.images.new('Bishop visibility diagnostic',width=2048,height=2048,alpha=False,float_buffer=True);image.colorspace_settings.name='Non-Color'
for node in nodes:node.select=False
target=nodes.new('ShaderNodeTexImage');target.image=image;target.select=True;nodes.active=target
scratch=bpy.data.images.new('Disposable visibility cut target',width=256,height=256,alpha=False)
for cut in {m for ob in objects for m in ob.data.materials if m and m!=main}:
    ns=cut.node_tree.nodes
    for node in ns:node.select=False
    target=ns.new('ShaderNodeTexImage');target.image=scratch;target.select=True;ns.active=target
for ob in s.objects:ob.select_set(False)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.cycles.samples=1;s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT',use_clear=True)
array=np.array(image.pixels[:],dtype=np.float32).reshape(2048,2048,4)[::-1].copy()
np.save(out/'visibility.npy',array[:,:,0])
image.filepath_raw=str(out/'visibility.exr');image.file_format='OPEN_EXR';image.save()
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'ray_tolerance_model_units':a.tolerance,'facing_start':a.facing_start,'facing_full':a.facing_full,'mask':'Conservative per-control-vertex ray visibility, interpolated and baked on evaluated geometry. Optional smooth-normal facing weight exposes grazing areas to an explicit continuity trial; actual fixed-view validation is mandatory.','statistics':stats,'source_unchanged':True},indent=2)+'\n')
print('BISHOP_VISIBILITY_BAKED',json.dumps(stats),flush=True)
