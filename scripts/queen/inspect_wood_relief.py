"""Separate procedural pores from pigment relief without changing the rig."""
from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'history/queen-mission-008/queen-rebuilt.blend'
digest='c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004'
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
for variant,mode in [('091-smooth-varnish','no_bump'),('092-pigment-relief-no-pores','no_pores')]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
 scene=bpy.context.scene;obj=editable_mesh(scene);mat=obj.data.materials[0]
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
 bump=bs.inputs['Normal'].links[0].from_node;mix=bump.inputs['Height'].links[0].from_node
 assert bump.type=='BUMP' and mix.type=='MIX_RGB'
 if mode=='no_bump':
  for socket in ['Normal','Coat Normal']:
   for connection in list(bs.inputs[socket].links):links.remove(connection)
 else:
  mix.inputs[0].default_value=0
 cfg=json.loads(scene['mission_material_config']);cfg['variant']=variant
 cfg['relief_isolation']={'baseline':source.relative_to(ROOT).as_posix(),'source_sha256':digest,'mode':mode,'roughness_lighting_and_color_unchanged':True,'diagnostic':'Distinguish grain coloration from normal-map and procedural pore effects.'}
 scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
 out=ROOT/'build/queen-mission'/variant;out.mkdir(parents=True,exist_ok=True)
 scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='OPTIX'
 if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
 bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
 print('RELIEF_ISOLATION_DONE',variant,flush=True)
