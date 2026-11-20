"""Capture actual BSDF responses for a diffuse-only environment study."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from diffuse_study import configure
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
spec={'directions':[[e,az] for e in [15,45,75] for az in range(0,360,45)]+[[-20,az] for az in range(0,360,90)],'sun_angle_degrees':30}
lights,disabled=configure(s,spec)
s.render.resolution_x=s.render.resolution_y=320;s.render.resolution_percentage=100;s.render.use_border=False
s.cycles.samples=32;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
def capture(name):
    s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(out/(name+'.exr')),check_existing=False)
    ar=np.array(im.pixels[:],dtype=np.float32).reshape(320,320,4)[::-1].copy();bpy.data.images.remove(im)
    np.save(out/(name+'.npy'),ar);return ar
base=capture('preserved-reflections')
for i,lamp in enumerate(lights):
    lamp.data.energy=1.;capture(f'basis-{i:02d}');lamp.data.energy=0
    print('DIFFUSE_BASIS_COMPLETE',i,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'basis':spec,'disabled_diffuse_lights':disabled,'samples':32,'size':320,'basis_energy':1,
 'note':'Actual real-material BSDF responses. Glossy lamp visibility and glossy environment are preserved; diffuse environment is fitted separately. These are unsaved diagnostic passes, not final renders.'},indent=2)+'\n')
print('DIFFUSE_RESPONSE_CAPTURE_COMPLETE',flush=True)
