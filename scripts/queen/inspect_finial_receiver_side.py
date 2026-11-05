"""Inspect the minimal finial receiver trial from the established side camera."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
out=ROOT/'build/queen-mission/088-minimal-finial-receivers'
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
scene=bpy.context.scene;camera=scene.camera
camera.data.shift_x=0;camera.data.shift_y=0;camera.data.sensor_fit='VERTICAL';camera.data.ortho_scale=6.6
camera.location=(0,-16,2.55);camera.rotation_euler=(Vector((0,0,2.55))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=600;scene.render.resolution_y=900
scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
scene.render.filepath=str(out/'wood-profile.png');bpy.ops.render.render(write_still=True)
clay=bpy.data.materials.new('Inspection clay');clay.use_nodes=True
bsdf=clay.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.24,.26,.29,1);bsdf.inputs['Roughness'].default_value=.32
set_material(scene,clay);scene.render.filepath=str(out/'neutral-profile.png');bpy.ops.render.render(write_still=True)
print('FINIAL_RECEIVER_SIDE_INSPECTED',flush=True)
