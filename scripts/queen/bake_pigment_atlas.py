"""Bake pigment only into one non-overlapping UV atlas, then restore real shading."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/012-projected-pigment/queen.blend');p.add_argument('--variant',default='013-pigment-atlas');p.add_argument('--texture',default='assets/queen/queen-pigment-albedo.png');p.add_argument('--reuse-uv',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
co=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',co);rings=co.reshape(-1,192,3)
r=np.linalg.norm(rings[:,:,:2],axis=2).mean(1);z=rings[:,:,2].mean(1)
arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];arc[0]=arc[1];arc-=arc[1];arc/=arc[-1]
uv=obj.data.uv_layers.get('Pigment atlas')
if args.reuse_uv:assert uv is not None,'A rebake must retain the existing pigment coordinates.'
else:
    uv=uv or obj.data.uv_layers.new(name='Pigment atlas')
    for face in obj.data.polygons:
        us=[((obj.data.loops[i].vertex_index%192)/192-.25)%1 for i in face.loop_indices]
        seam=max(us)-min(us)>.5
        for li,u in zip(face.loop_indices,us):
            ri=obj.data.loops[li].vertex_index//192
            uv.data[li].uv=(u+(1 if seam and u<.5 else 0),float(arc[ri]))
obj.data.uv_layers.active=uv;uv.active_render=True
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
color=bs.inputs['Base Color'].links[0].from_socket
emission=nodes.new('ShaderNodeEmission');links.new(color,emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
atlas=bpy.data.images.new('Queen pigment atlas',width=2048,height=2048,alpha=False);atlas.colorspace_settings.name='sRGB'
target=nodes.new('ShaderNodeTexImage');target.image=atlas;target.label='Baked pigment only, no lighting'
for node in nodes:node.select=False
target.select=True;nodes.active=target
for selected in bpy.context.selected_objects:selected.select_set(False)
obj.select_set(True);bpy.context.view_layer.objects.active=obj
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
scene.cycles.samples=1;scene.render.bake.margin=8
bpy.ops.object.bake(type='EMIT',use_clear=True)
atlaspath=ROOT/args.texture;atlas.filepath_raw=str(atlaspath);atlas.file_format='PNG';atlas.save();atlas.pack()
# All subsequent images are real BSDF renders with movable lights and camera.
links.new(bs.outputs['BSDF'],output.inputs['Surface']);nodes.remove(emission)
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;links.new(uvnode.outputs['UV'],target.inputs['Vector'])
links.new(target.outputs['Color'],bs.inputs['Base Color'])
cfg=json.loads(scene['mission_material_config']);cfg.update({'variant':args.variant,'source':args.source,'texture':args.texture,'uv_layer':uv.name,'image_mix':1,'value':1,'saturation':1,'atlas_size':2048,'atlas_bakes_lighting':False,'atlas_reused_uv':args.reuse_uv})
scene['mission_material_config']=json.dumps(cfg,sort_keys=True);scene['mission_variant']=cfg['variant']
scene.cycles.samples=64;scene.cycles.use_denoising=True
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();cfg['texture_sha256']=hashlib.sha256(atlaspath.read_bytes()).hexdigest()
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('PIGMENT_ATLAS_DONE',flush=True)
