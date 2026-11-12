"""Measure localized collar reflections without changing the accepted scene."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', default='build/bishop-mission/111-collar-spots')
p.add_argument('--samples', type=int, default=128)
p.add_argument('--beam', type=float, default=2)
a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
source = ROOT / 'history/bishop-mission-013/bishop-rebuilt.blend'
out = ROOT / a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
folder = ROOT/'build/bishop-mission/108-collar-normals'
geometry = json.loads((folder/'geometry.json').read_text())
normals = json.loads((folder/'manifest.json').read_text())
assert geometry['_provenance']['source_sha256'] == normals['source_sha256'] == digest
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
s = bpy.context.scene
view = np.array(s.camera.matrix_world.to_3x3() @ Vector((0,0,1)))
view /= np.linalg.norm(view)
specs, lamps = [], []
for i, (name, record) in enumerate(normals['points'].items()):
    n = np.array(record['normal']); n /= np.linalg.norm(n)
    point = np.array(geometry[name]['surface'])
    direction = 2*np.dot(n, view)*n-view
    spec = dict(name='collar arc '+str(i+1), type='SPOT', energy=100,
                color=[1,.97,.88], position=(point+7*direction).tolist(),
                target=point.tolist(), spot_size=math.radians(a.beam),
                spot_blend=.6, shadow_soft_size=.025,
                diffuse=False, glossy=True, receiver='body')
    assert spec['name'] not in bpy.data.objects
    data = bpy.data.lights.new(spec['name'], 'SPOT')
    lamp = bpy.data.objects.new(spec['name'], data)
    s.collection.objects.link(lamp)
    lamp.location = spec['position']
    lamp.rotation_euler = (Vector(spec['target'])-lamp.location).to_track_quat('-Z','Y').to_euler()
    for key in ['spot_size','spot_blend','shadow_soft_size']:
        setattr(data, key, spec[key])
        assert np.isclose(getattr(data,key),spec[key],rtol=2e-6)
    data.energy = 0
    data.color = (1,1,1)
    lamp.visible_diffuse = False
    lamp.visible_glossy = True
    lamp.light_linking.receiver_collection = bpy.data.collections['Bishop light receiver body']
    lamps.append(lamp); specs.append(spec)
box = [280,360,700,660]
w,h = s.render.resolution_x,s.render.resolution_y
s.render.resolution_percentage = 100
s.render.use_border = True; s.render.use_crop_to_border = False
s.render.border_min_x=box[0]/w; s.render.border_max_x=box[2]/w
s.render.border_min_y=1-box[3]/h; s.render.border_max_y=1-box[1]/h
s.render.image_settings.file_format='OPEN_EXR'
s.render.image_settings.color_mode='RGBA'; s.render.image_settings.color_depth='32'
s.cycles.samples=a.samples; s.cycles.use_adaptive_sampling=False; s.cycles.use_denoising=True
s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
def render(label):
    path=out/(label+'.exr'); s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False)
    pixels=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy()
    np.save(out/(label+'.npy'),pixels)
    bpy.data.images.remove(im)
    print('COLLAR_SPOT_PASS',label,flush=True)
render('base')
for i,lamp in enumerate(lamps):
    lamp.data.energy=100; render('lamp-'+str(i+1)); lamp.data.energy=0
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
config=dict(source=source.relative_to(ROOT).as_posix(), variant='112-collar-spots',
            samples=128, adaptive_sampling=False, lights=specs,
            hypothesis='Localized warm-white collar reflections at measured BSDF normals; all accepted lamps unchanged.')
(out/'manifest.json').write_text(json.dumps(dict(source=config['source'],source_sha256=digest,
 config=config, samples=a.samples, fixed_samples=True, border=box, source_unchanged=True,
 normal_measurement='build/bishop-mission/108-collar-normals/manifest.json',
 note='Unsaved real-BSDF diagnostic passes. No public model or review change.'),indent=2)+'\n',newline='\n')
print('COLLAR_SPOT_BASIS_COMPLETE',flush=True)
