"""Local profile edits on a saved accepted queen, preserving camera/material/UVs."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(args.config).read_text())
source=ROOT/cfg['source'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
co=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',co);rings=co.reshape(-1,192,3)
for key,(dr,dz) in cfg.get('ring_offsets',{}).items():
    i=int(key);oldr=np.linalg.norm(rings[i,:,:2],axis=1);rings[i,:,:2]*=((oldr+dr)/oldr)[:,None];rings[i,:,2]+=dz
for key,(r,z) in cfg.get('profiles',{}).items():
    i=int(key);oldr=np.linalg.norm(rings[i,:,:2],axis=1);rings[i,:,:2]*=(r/oldr)[:,None]
    rings[i,:,2]+=z-float(rings[i,:,2].mean())
obj.data.vertices.foreach_set('co',rings.reshape(-1));obj.data.update()
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=cfg.get('samples',32);scene.cycles.use_denoising=True
scene['mission_variant']=cfg['variant'];bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('Mission inspection clay');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
obj.data.materials[0]=mat;scene.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('GEOMETRY_TRIAL_DONE',cfg['variant'],flush=True)
