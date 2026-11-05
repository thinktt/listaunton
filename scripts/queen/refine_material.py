"""Trial continuous grain coordinates and surface-dependent polish on the queen."""
from pathlib import Path
import argparse,json,sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--variant',required=True);p.add_argument('--lights',action='store_true');p.add_argument('--samples',type=int,default=32)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
refined=args.variant.startswith(('006','007'))
warm=args.variant.startswith('007')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/args.source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coords)
rings=coords.reshape((-1,192,3));r=np.linalg.norm(rings[:,:,:2],axis=2).mean(1);z=rings[:,:,2].mean(1)
arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];arc[0]=arc[1] # underside center does not consume face-grain distance
arc-=arc[1]
uv=obj.data.uv_layers.get('Turned wood') or obj.data.uv_layers.new(name='Turned wood')
for face in obj.data.polygons:
 us=[((obj.data.loops[i].vertex_index%192)/192-.25)%1 for i in face.loop_indices]
 seam=max(us)-min(us)>.5
 for li,u in zip(face.loop_indices,us):
  ri=obj.data.loops[li].vertex_index//192
  uv.data[li].uv=((u+(1 if seam and u<.5 else 0))*(1.5 if refined else 1),float(arc[ri]/(3.5 if refined else 5.5)+.13))
mat=obj.data.materials[0];mat.name='Walnut - continuous turned grain'
nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF')
grain=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image)
grain.projection='FLAT';grain.extension='REPEAT'
tex=nodes.new('ShaderNodeUVMap');tex.uv_map='Turned wood';tex.label='Continuous circumference and meridian distance'
links.new(tex.outputs['UV'],grain.inputs['Vector'])
if refined:
    color_links=list(grain.outputs['Color'].links)
    grade=nodes.new('ShaderNodeHueSaturation');grade.inputs['Saturation'].default_value=.98 if warm else .75;grade.inputs['Value'].default_value=1.0 if warm else .9
    links.new(grain.outputs['Color'],grade.inputs['Color'])
    for link in color_links:
        if link.to_node.type=='MIX_RGB':
            target_node,target_socket=link.to_node,link.to_socket
            if warm:target_node.inputs[0].default_value=.60
            links.new(grade.outputs['Color'],target_socket)
gray=nodes.new('ShaderNodeRGBToBW');links.new(grain.outputs['Color'],gray.inputs['Color'])
rough=nodes.new('ShaderNodeMapRange');rough.label='Grain-driven polish'
rough.inputs['From Min'].default_value=.02;rough.inputs['From Max'].default_value=.24
rough.inputs['To Min'].default_value=.22 if refined else .32;rough.inputs['To Max'].default_value=.11 if refined else .18
links.new(gray.outputs[0],rough.inputs['Value']);links.new(rough.outputs[0],bs.inputs['Roughness'])
bs.inputs['Coat Weight'].default_value=.28 if refined else .20;bs.inputs['Coat Roughness'].default_value=.09 if refined else .18
bump=next(n for n in nodes if n.type=='BUMP');bump.inputs['Strength'].default_value=.10 if refined else .16;bump.inputs['Distance'].default_value=.008
if warm:
 rough.inputs['To Min'].default_value=.24;rough.inputs['To Max'].default_value=.14
 bs.inputs['Coat Weight'].default_value=.4;bs.inputs['Coat Roughness'].default_value=.1
 bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.012
if args.lights:
 specs={'Key - upper left':((-1.4,-4,9),500,.65),'Front right soft highlight':((3,-5,7),160,.7),'Gentle rim':((2,3,7),35,1.8)}
 if refined:
  specs={'Key - upper left':((-1.4,-4,9),650,.5),'Front right soft highlight':((3,-5,7),350,.55),'Gentle rim':((2,3,7),220,.8)}
 if warm:
  specs={'Key - upper left':((-1,-.3,12),1100,.9),'Front right soft highlight':((3,-5,7),400,.8),'Gentle rim':((3,1,3),140,.6)}
 for name,(loc,energy,size) in specs.items():
  light=bpy.data.objects[name];light.location=loc;light.data.energy=energy;light.data.size=size
  light.rotation_euler=(Vector((0,0,2.3))-light.location).to_track_quat('-Z','Y').to_euler()
 scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.05
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100
scene.render.filepath=str(out/'wood.png');scene['mission_variant']=args.variant
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e)
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source':args.source,'uv_meridian_scale':3.5 if refined else 5.5,'uv_repeat_u':1.5 if refined else 1,'uv_offset_v':.13,'bump_strength':.1 if refined else .16,'bump_distance':.008,'lights_changed':args.lights,'samples':args.samples},indent=2))
print('MATERIAL_TRIAL_DONE',args.variant,flush=True)
