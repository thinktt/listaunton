"""Reproducible localized queen refinements from the accepted mission baseline."""
from pathlib import Path
import argparse,json,sys
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--variant',default='001-collars')
parser.add_argument('--samples',type=int,default=24)
parser.add_argument('--config')
parser.add_argument('--lower-radius-delta',type=float,default=-.004)
parser.add_argument('--silhouette-only',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
baseline=ROOT/'history/queen-mission-start/queen-rebuilt.blend'
bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False)
scene=bpy.context.scene
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
obj.data.vertices.foreach_get('co',coords);rings=coords.reshape((-1,192,3))
profiles={
50:(.431,2.760),51:(.523,2.790),52:(.606,2.800),53:(.650,2.825),
54:(.672,2.855),55:(.676,2.884),56:(.672,2.915),57:(.656,2.940),
58:(.630,2.953),59:(.598,2.954),60:(.568,2.955),61:(.551,2.960),
62:(.547,2.980),63:(.555,3.000),64:(.579,3.018),65:(.607,3.032),
66:(.620,3.052),67:(.622,3.075),68:(.615,3.098),69:(.599,3.116),
70:(.575,3.125),71:(.540,3.127),72:(.505,3.130),73:(.462,3.140),
74:(.448,3.165),75:(.449,3.190),76:(.466,3.211),77:(.478,3.231),
78:(.481,3.255),79:(.476,3.280),80:(.465,3.298),81:(.450,3.310),
82:(.428,3.315),83:(.425,3.330),84:(.432,3.370),85:(.445,3.430),
86:(.467,3.520),87:(.487,3.620),88:(.509138,3.736771),
}
if args.variant!='001-collars':
    profiles.update({
      53:(.646,2.825),54:(.665,2.855),55:(.669,2.884),56:(.665,2.915),
      57:(.650,2.940),58:(.625,2.953),59:(.590,2.954),60:(.552,2.955),
      61:(.530,2.960),62:(.522,2.975),63:(.530,2.985),
      64:(.550,2.989),65:(.570,3.005),66:(.582,3.026),67:(.584,3.049),
      68:(.580,3.073),69:(.565,3.094),70:(.545,3.105),71:(.515,3.109),
      72:(.480,3.115),73:(.435,3.140),74:(.423,3.165),75:(.425,3.190),
    })
if args.config:
    profiles={int(k):v for k,v in json.loads(Path(args.config).read_text())['profiles'].items()}
if args.variant.startswith('003'):
    profiles={i:rz for i,rz in profiles.items() if i>=64}
    for i,w in {53:.25,54:.8,55:1.,56:1.,57:.8,58:.25}.items():
        profiles[i]=(float(np.linalg.norm(rings[i,:,:2],axis=1).mean())+args.lower_radius_delta*w,float(rings[i,:,2].mean()))
for i,(r,z) in profiles.items():
    oldr=np.linalg.norm(rings[i,:,:2],axis=1)
    rings[i,:,:2]*=(r/oldr)[:,None]
    if i>=89:rings[i,:,2]+=z-float(rings[i,:,2].mean())
    else:rings[i,:,2]=z
crown_adjustments={}
if args.variant.startswith('002'):
    # Broader lip surface; a shallower bowl; a compact seated egg.
    for i,dr in ({97:-.015,98:-.045,99:-.040,100:-.025,101:-.012} if args.variant=='002-crown' else {}).items():
        oldr=np.linalg.norm(rings[i,:,:2],axis=1)
        rings[i,:,:2]*=((oldr+dr)/oldr)[:,None]
    if args.variant=='002-crown':
        for i,dz in {103:.045,104:.070,105:.085,106:.090,107:.085}.items():rings[i,:,2]+=dz
    else:
        for i,z in {100:4.105,101:4.080,102:4.055,103:4.035,104:4.020,105:4.012,106:4.015,107:4.022}.items():
            rings[i,:,2]+=z-float(rings[i,:,2].mean())
    oldbase=float(rings[108,:,2].mean());oldtop=float(rings[-1,:,2].mean())
    newbase=4.088 if args.variant=='002-crown' else 4.045;newtop=oldtop-.026
    rings[108:,:,:2]*=.95
    rings[108:,:,2]=newbase+(rings[108:,:,2]-oldbase)*(newtop-newbase)/(oldtop-oldbase)
    crown_adjustments={'finial_base':newbase,'finial_top':newtop,'finial_radius_scale':.95,'bowl_raised':True,'inner_lip_inset':args.variant=='002-crown'}
obj.data.vertices.foreach_set('co',rings.reshape(-1));obj.data.update()
scene['mission_variant']=args.variant
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
scene.render.resolution_percentage=100
scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
scene.render.image_settings.color_mode='RGBA'
scene.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
if args.silhouette_only:
    silhouette=bpy.data.materials.new('Silhouette inspection');silhouette.use_nodes=True
    tree=silhouette.node_tree;tree.nodes.clear()
    output=tree.nodes.new('ShaderNodeOutputMaterial');emission=tree.nodes.new('ShaderNodeEmission')
    tree.links.new(emission.outputs[0],output.inputs['Surface']);obj.data.materials[0]=silhouette
    scene.cycles.max_bounces=0
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e)
bpy.ops.render.render(write_still=True)
if args.silhouette_only:
    (out/'parameters.json').write_text(json.dumps({'variant':args.variant,'profiles':profiles,'lower_radius_delta':args.lower_radius_delta,'samples':args.samples},indent=2))
    print('SILHOUETTE_TRIAL_DONE',args.variant,flush=True)
    sys.exit(0)
clay=bpy.data.materials.new('Mission inspection clay');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
obj.data.materials[0]=clay
scene.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'variant':args.variant,'profiles':profiles,'crown_adjustments':crown_adjustments,'samples':args.samples},indent=2))
print('MISSION_TRIAL_DONE',args.variant,flush=True)
