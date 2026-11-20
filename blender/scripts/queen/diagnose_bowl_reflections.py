"""Isolate the current bowl reflection without changing the accepted scene."""
from pathlib import Path
import sys,json,hashlib
import bpy
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'history/queen-mission-010/queen-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='6bbc7d1dbeffd54e846895eb1f9f3854092c8b57d4267fa49c621e7f67e74325'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene
lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights}
out=ROOT/'build/queen-mission/099-bowl-diagnostics';out.mkdir(parents=True,exist_ok=True)
s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
cases={
 'without-bowl-reflectors':lambda o:'bowl-' in o.name,
 'without-rim-reflectors':lambda o:'rim-front-' in o.name,
 'without-finial-spots':lambda o:'finial-' in o.name and o.data.type=='SPOT',
 'diffuse-only':lambda o:not o.visible_diffuse,
}
for label,exclude in cases.items():
 for light in lights:light.data.energy=0 if exclude(light) else powers[light.name]
 s.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
 print('DIAGNOSTIC_DONE',label,flush=True)
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':list(cases),'samples':64,'source_unchanged':True},indent=2))
