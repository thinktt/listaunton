"""Isolate socket polish/relief at fixed camera; never save diagnostic shaders."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/087-socket-finish-probe')
p.add_argument('--samples',type=int,default=256)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/a.source; out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest()
variants=[('control',{}),('no-coat-bump',{'coat_geometric':True}),
          ('third-relief',{'relief_distance':.003}),
          ('smooth-coat-018',{'coat_geometric':True,'coat_roughness':.18}),
          ('no-relief',{'relief_distance':0})]
records=[]
for label,change in variants:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene
    mat=next(m for m in bpy.data.materials if 'inferred boxwood pigment' in m.name)
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    bs=nodes['Principled BSDF']; bump=nodes['Wood micro relief']
    if change.get('coat_geometric'):
        for link in list(bs.inputs['Coat Normal'].links): links.remove(link)
    if 'relief_distance' in change: bump.inputs['Distance'].default_value=change['relief_distance']
    if 'coat_roughness' in change: bs.inputs['Coat Roughness'].default_value=change['coat_roughness']
    s.render.resolution_percentage=100
    s.render.use_border=True; s.render.use_crop_to_border=False
    s.render.border_min_x=330/1254; s.render.border_max_x=660/1254
    s.render.border_min_y=1-885/1254; s.render.border_max_y=1-710/1254
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
    s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples; s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    s.render.filepath=str(out/(label+'.png'))
    bpy.ops.render.render(write_still=True)
    records.append({'label':label,'change':change,'render_sha256':hashlib.sha256((out/(label+'.png')).read_bytes()).hexdigest()})
    print('SOCKET_FINISH_PROBE',label,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'samples':a.samples,'crop':[330,710,660,885],'fixed_camera':True,'diagnostics_only':True,
 'note':'Unsaved global material isolations, viewed only at the socket; not acceptance candidates.',
 'variants':records},indent=2)+'\n')
