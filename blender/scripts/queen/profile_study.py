"""Controlled shape/camera studies from a recorded accepted queen checkpoint.

Every trial is a real shaded mesh. Source, registration and UVs stay intact.
Camera experiments use a physical axial scale, recorded separately from local
meridian edits; the 54-degree local studies keep all heights unchanged.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh, set_material, render_meshes
from refine_socket_flare import read_controls, replace_meridian

SOURCE_SHA = '8420d47bbbd8cb86c1eee77e5b326f945fe57b4e3acf7d30e18414f9aa0864c6'

def main():
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('--render',action='store_true');p.add_argument('--samples',type=int,default=64)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    cfg=json.loads(a.config.read_text());source=ROOT/cfg.get('source_archive','history/queen-mission-018/queen-rebuilt.blend')
    if not source.exists():source=ROOT/'models/queen/queen-rebuilt.blend'
    source_sha=cfg.get('source_sha256',SOURCE_SHA)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
    out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;o=editable_mesh(s);settings=json.loads(s['mission_material_config'])
    before=read_controls(o.data,int(o['ring_segments']));after=before.copy()
    for key,radius in cfg.get('radii',{}).items():
        i=int(key);after[i,:,:2] *= (radius/np.linalg.norm(after[i,:,:2],axis=1))[:,None]
    for key,delta in cfg.get('z_offsets',{}).items():after[int(key),:,2]+=delta
    if cfg.get('radii') or cfg.get('z_offsets'):
        boundary=replace_meridian(s,o,settings,after,preserve_face_assignments=cfg.get('preserve_face_assignments',False))
        settings['raised_flare_compact_socket']['socket_partition']=boundary
    angle=cfg.get('elevation',54)
    axial=cfg.get('axial_scale',1)
    for obj in [o]+render_meshes(s):
        if obj is o and obj in render_meshes(s):continue
        obj.matrix_world=Matrix.Diagonal((1,1,axial,1))@obj.matrix_world
    # The camera remains centered on the same board point. Its vertical shift
    # compensates only the changed projection of the unchanged foot diameter.
    cam=s.camera
    if angle!=54:
        fit=json.loads((ROOT/'assets/queen/finish-fit.json').read_text())
        el=math.radians(angle)
        # Keep the registered floor after compensating the foot ellipse.
        dy=(math.sin(math.radians(54))-math.sin(el))*1.03671
        target=Vector((0,0,((fit['camera_floor']+cfg.get('camera_floor_offset',0)-s.render.resolution_y/2)/fit['camera_scale']+dy)/math.cos(el)))
        cam.location=target+Vector((0,-12*math.cos(el),12*math.sin(el)))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    settings[cfg.get('feature_key','profile_study')]={'source_sha256':source_sha,'config':cfg,'control_sha256':hashlib.sha256(after.tobytes()).hexdigest()}
    settings['variant']=cfg['variant'];s['mission_material_config']=json.dumps(settings)
    s['mission_variant']=cfg['variant'];s.render.use_persistent_data=True
    bpy.context.view_layer.update()
    np.savez(out/'controls.npz',before=before,after=after)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'),compress=True)
    if not a.render:return
    # Reopen so the fitted wood is judged in its saved state.
    bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
    s=bpy.context.scene;cam=s.camera;o=editable_mesh(s);wood=o.data.materials[0]
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False;s.cycles.use_light_tree=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type=='OPTIX'
    if any(dev.use for dev in prefs.devices):s.cycles.device='GPU'
    clay=bpy.data.materials.new('Profile study clay');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
    for view in ('fixed','side'):
        if view=='side':
            cam.data.shift_x=cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.6
            cam.location=(0,-16,2.55);cam.rotation_euler=(Vector((0,0,2.55))-cam.location).to_track_quat('-Z','Y').to_euler()
            s.render.resolution_x=600;s.render.resolution_y=900
        for label,mat in [('wood',wood),('clay',clay)]:
            set_material(s,mat);s.render.filepath=str(out/(('wood.png' if label=='wood' else 'clay.png') if view=='fixed' else f'side-{label}.png'))
            bpy.ops.render.render(write_still=True)
    print('PROFILE_STUDY_RENDERED',cfg['variant'],flush=True)

if __name__=='__main__':main()
