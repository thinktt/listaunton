"""Build a reproducible wood/lighting trial without overwriting accepted assets."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
config_path=Path(args.config);cfg=json.loads(config_path.read_text())
source=ROOT/cfg['source'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
co=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',co)
rings=co.reshape(-1,192,3);r=np.linalg.norm(rings[:,:,:2],axis=2).mean(1);z=rings[:,:,2].mean(1)
arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];arc[0]=arc[1];arc-=arc[1]
uv=obj.data.uv_layers.get('Turned wood') or obj.data.uv_layers.new(name='Turned wood')
for face in obj.data.polygons:
    us=[((obj.data.loops[i].vertex_index%192)/192-.25)%1 for i in face.loop_indices]
    seam=max(us)-min(us)>.5
    for li,u in zip(face.loop_indices,us):
        ri=obj.data.loops[li].vertex_index//192
        uv.data[li].uv=((u+(1 if seam and u<.5 else 0))*cfg['uv_repeat_u'],float(arc[ri]/cfg['uv_meridian_scale']+cfg['uv_offset_v']))
mat=obj.data.materials[0];mat.name='Walnut - fine turned grain';tree=mat.node_tree;nodes=tree.nodes;links=tree.links
bs=nodes.get('Principled BSDF');grain=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image)
texture=ROOT/cfg['texture'];image=bpy.data.images.load(str(texture),check_existing=False);image.pack()
grain.image=image;grain.projection='FLAT';grain.extension='REPEAT'
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='Turned wood';links.new(uvnode.outputs['UV'],grain.inputs['Vector'])
targets=[(link.to_node,link.to_socket) for link in list(grain.outputs['Color'].links) if link.to_node.type=='MIX_RGB']
grade=nodes.new('ShaderNodeHueSaturation');grade.inputs['Saturation'].default_value=cfg['saturation'];grade.inputs['Value'].default_value=cfg['value'];links.new(grain.outputs['Color'],grade.inputs['Color'])
for node,socket in targets:
    node.inputs[0].default_value=cfg['image_mix'];links.new(grade.outputs['Color'],socket)
gray=nodes.new('ShaderNodeRGBToBW');links.new(grain.outputs['Color'],gray.inputs['Color'])
rough=nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=.02;rough.inputs['From Max'].default_value=.24
rough.inputs['To Min'].default_value=cfg['rough_dark'];rough.inputs['To Max'].default_value=cfg['rough_light']
links.new(gray.outputs[0],rough.inputs['Value']);links.new(rough.outputs[0],bs.inputs['Roughness'])
bs.inputs['Coat Weight'].default_value=cfg['coat'];bs.inputs['Coat Roughness'].default_value=cfg['coat_roughness']
bump=next(n for n in nodes if n.type=='BUMP');bump.inputs['Strength'].default_value=cfg['bump_strength'];bump.inputs['Distance'].default_value=cfg['bump_distance']
if cfg.get('image_bump'):links.new(gray.outputs[0],bump.inputs['Height'])
if cfg.get('pore_noise'):
    texcoord=nodes.new('ShaderNodeTexCoord');pores=nodes.new('ShaderNodeTexNoise')
    pores.inputs['Scale'].default_value=cfg['pore_noise'];pores.inputs['Detail'].default_value=2
    pores.inputs['Roughness'].default_value=.7;links.new(texcoord.outputs['Object'],pores.inputs['Vector'])
    relief=nodes.new('ShaderNodeMixRGB');relief.inputs[0].default_value=cfg['pore_mix']
    links.new(gray.outputs[0],relief.inputs[1]);links.new(pores.outputs['Fac'],relief.inputs[2]);links.new(relief.outputs[0],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],bs.inputs['Coat Normal'])
for light in list(scene.objects):
    if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
for spec in cfg['lights']:
    data=bpy.data.lights.new(spec['name'],'AREA');data.energy=spec['energy'];data.shape='DISK';data.size=spec['size']
    light=bpy.data.objects.new(spec['name'],data);scene.collection.objects.link(light);light.location=spec['position']
    light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=cfg['world']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.cycles.samples=cfg['samples'];scene.cycles.use_denoising=True;scene.render.resolution_percentage=100
scene.render.filepath=str(out/'wood.png');scene['mission_variant']=cfg['variant'];scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True)
cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();cfg['texture_sha256']=hashlib.sha256(texture.read_bytes()).hexdigest()
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('CONFIG_MATERIAL_DONE',cfg['variant'],flush=True)
