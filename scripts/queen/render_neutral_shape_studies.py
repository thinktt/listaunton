"""Render recorded Queen profiles with a shared, neutral diagnostic light rig.

This does not save or promote a model. Production subdivision is retained.
The existing fitted wood/light receivers are hidden only in this temporary
scene; use study_compact_turning.py for a real material acceptance render.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from refine_socket_flare import read_controls

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--variant',help='Optional single recorded variant, or baseline')
    p.add_argument('--samples',type=int,default=24)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=a.source.resolve();source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
    configs=json.loads(a.manifest.read_text())
    assert configs and all(c['source_sha256']==source_sha for c in configs)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;body=editable_mesh(scene)
    before=read_controls(body.data,int(body['ring_segments']))
    for obj in scene.objects:
        if obj.type in {'MESH','LIGHT'}:obj.hide_render=obj!=body
    body.hide_set(False)
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
    clay=bpy.data.materials.new('Queen geometry study clay');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=(.28,.31,.35,1)
    bs.inputs['Roughness'].default_value=.38
    body.data.materials.clear();body.data.materials.append(clay)
    for poly in body.data.polygons:poly.material_index=0
    for name,loc,power,size in [('key',(-4,-5,8),650,4),('fill',(5,-1,5),380,4),('rim',(-2,4,6),600,3)]:
        data=bpy.data.lights.new('Study '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        obj=bpy.data.objects.new('Study '+name,data);scene.collection.objects.link(obj);obj.location=loc
        obj.rotation_euler=(Vector((0,0,2))-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.2,.2,.2,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
    scene.render.engine='CYCLES';scene.cycles.samples=a.samples
    scene.cycles.use_denoising=True;scene.cycles.use_adaptive_sampling=False;scene.cycles.use_light_tree=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    scene.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
    cam=scene.camera
    saved=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y,cam.data.sensor_fit)
    entries=[{'variant':'baseline','angle':54,'floor':860.223491056495}]+configs
    if a.variant:
        entries=[c for c in entries if c['variant']==a.variant]
        assert entries,'Unknown study variant'
    for cfg in entries:
        tag=cfg['variant'];assert Path(tag).name==tag
        after=before.copy()
        for key,radius in cfg.get('ring_radii',{}).items():
            i=int(key);after[i,:,:2]*=(float(radius)/np.linalg.norm(after[i,:,:2],axis=1))[:,None]
        for key,dz in cfg.get('ring_z_offsets',{}).items():after[int(key),:,2]+=float(dz)
        assert np.isfinite(after).all()
        body.data.vertices.foreach_set('co',after.astype(np.float32).ravel());body.data.update()
        cam.location,cam.rotation_euler,cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y,cam.data.sensor_fit=saved
        scene.render.resolution_x=scene.render.resolution_y=1254
        angle=math.radians(cfg['angle'])
        if cfg['angle']!=54:
            target=Vector((0,0,(cfg['floor']-627)/(264.61125*math.cos(angle))))
            cam.location=target+Vector((0,-12*math.cos(angle),12*math.sin(angle)))
            cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        out=a.output.resolve()/tag;out.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(out/'fixed-neutral.png');bpy.ops.render.render(write_still=True)
        cam.data.shift_x=cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.6
        cam.location=(0,-16,2.55);cam.rotation_euler=(Vector((0,0,2.55))-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.resolution_x,scene.render.resolution_y=600,900
        scene.render.filepath=str(out/'side-neutral.png');bpy.ops.render.render(write_still=True)
        (out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
        print('NEUTRAL_STUDY_RENDERED',tag,flush=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha

if __name__=='__main__':main()
