"""Controlled king trials. Run in Blender; accepted assets are never overwritten."""
from pathlib import Path
import argparse, hashlib, json, math, sys
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def gpu(scene):
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX'; prefs.get_devices()
        for dev in prefs.devices: dev.use=dev.type=='OPTIX'
        if any(dev.use for dev in prefs.devices): scene.cycles.device='GPU'
    except Exception as exc: print('CPU fallback:',exc)

def meshes(scene):
    return [ob for ob in scene.objects if ob.type=='MESH' and not ob.hide_render]

def procedural_material(cfg):
    mat=bpy.data.materials.new('King walnut - turned grain')
    mat.use_nodes=True; n=mat.node_tree.nodes; l=mat.node_tree.links
    bs=n.get('Principled BSDF'); bs.inputs['Roughness'].default_value=cfg.get('roughness',.29)
    bs.inputs['Coat Weight'].default_value=cfg.get('coat',.3)
    bs.inputs['Coat Roughness'].default_value=cfg.get('coat_roughness',.2)
    bs.inputs['Specular IOR Level'].default_value=.35
    coord=n.new('ShaderNodeTexCoord')
    scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(4,4,48)
    l.new(coord.outputs['Object'],scale.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1
    noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.72
    l.new(scale.outputs['Vector'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.name='Walnut pigment'
    ramp.color_ramp.elements[0].position=.23;ramp.color_ramp.elements[0].color=(.021,.0065,.0019,1)
    ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.185,.061,.017,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    pores=n.new('ShaderNodeTexNoise');pores.inputs['Scale'].default_value=280;pores.inputs['Detail'].default_value=2
    l.new(coord.outputs['Object'],pores.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.002
    l.new(pores.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat

def lights(scene,cfg):
    for ob in list(scene.objects):
        if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
    for row in cfg['lights']:
        data=bpy.data.lights.new(row['name'],'AREA');data.energy=row['energy'];data.shape=row.get('shape','DISK');data.size=row['size']
        if data.shape=='RECTANGLE':data.size_y=row.get('size_y',row['size'])
        ob=bpy.data.objects.new(row['name'],data);scene.collection.objects.link(ob);ob.location=row['position']
        ob.rotation_euler=(Vector(row.get('target',[0,0,2.5]))-ob.location).to_track_quat('-Z','Y').to_euler()
        ob.visible_diffuse=row.get('diffuse',True);ob.visible_glossy=row.get('glossy',True)
    bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(1,1,1,1);bg.inputs[1].default_value=cfg.get('world',.12)

def run(cfg):
    source=ROOT/cfg['source'];source_hash=sha(source)
    if cfg.get('source_sha256'):assert cfg['source_sha256']==source_hash
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;objects=meshes(scene);assert len(objects)==2
    axis=scene.camera.matrix_world.to_3x3()@Vector((0,0,1))
    elevation=math.degrees(math.asin(axis.z));assert abs(elevation-54)<.001,elevation
    body=next(ob for ob in objects if 'body' in ob.name)
    if cfg.get('profile_offsets'):
        co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
        for index,offset in cfg['profile_offsets'].items():
            j=int(index);r=np.linalg.norm(co[j,:,:2],axis=1)
            co[j,:,:2]*=((r+offset[0])/r)[:,None];co[j,:,2]+=offset[1]
        body.data.vertices.foreach_set('co',co.reshape(-1));body.data.update()
    if cfg.get('procedural'):
        mat=procedural_material(cfg)
        for ob in objects:ob.data.materials.clear();ob.data.materials.append(mat)
    if cfg.get('coat_microrelief'):
        mat=objects[0].data.materials[0];nodes=mat.node_tree.nodes
        bump=nodes['Pigment microrelief'];bs=nodes.get('Principled BSDF')
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Coat Normal'])
        bump.inputs['Strength'].default_value=cfg.get('relief_strength',.1)
        bump.inputs['Distance'].default_value=cfg.get('relief_distance',.002)
    if cfg.get('lights'):lights(scene,cfg)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    scene.render.engine='CYCLES';scene.cycles.samples=cfg.get('samples',48);scene.cycles.use_denoising=True
    scene.render.film_transparent=True;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.use_persistent_data=True;gpu(scene)
    scene['king_mission_variant']=cfg['variant'];scene['reconstruction']='King, assumed 54 degree orthographic camera; original sprites authoritative.'
    scene['king_mission_config']=json.dumps(cfg,sort_keys=True)
    scene.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'king.blend'))
    bpy.ops.render.render(write_still=True)
    cfg.update(source_sha256=source_hash,model_sha256=sha(out/'king.blend'),elevation_degrees=elevation)
    if cfg.get('neutral',True):
        old=[ob.data.materials[0] for ob in objects]
        clay=bpy.data.materials.new('King mission inspection clay');clay.use_nodes=True
        bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
        for ob in objects:ob.data.materials[0]=clay
        scene.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
        for ob,mat in zip(objects,old):ob.data.materials[0]=mat
    if cfg.get('profile',True):
        camera=scene.camera;camera.data.shift_x=0;camera.data.shift_y=0;camera.data.sensor_fit='VERTICAL';camera.data.ortho_scale=6
        camera.location=(0,-16,2.65);camera.rotation_euler=(Vector((0,0,2.65))-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.filepath=str(out/'profile.png');bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
    print('KING_TRIAL_DONE',cfg['variant'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(Path(args.config).read_text(encoding='utf-8')))
