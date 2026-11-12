"""Measure localized roughness variation in actual BSDF base crops; never save it."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--fields',default='build/bishop-mission/126-polish-fields/manifest.json')
p.add_argument('--out',default='build/bishop-mission/127-polish-probe')
p.add_argument('--samples',type=int,default=512)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);manifest=json.loads((ROOT/a.fields).read_text())
source=ROOT/manifest['source'];out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source)==manifest['source_sha256'];records=[]
for cfg in [dict(label='control'),*manifest['variants']]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    mat=next(m for m in bpy.data.materials if 'inferred boxwood pigment' in m.name)
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF']
    assert not bs.inputs['Roughness'].is_linked and not bs.inputs['Coat Roughness'].is_linked
    assert abs(bs.inputs['Roughness'].default_value-.23)<1e-6 and abs(bs.inputs['Coat Roughness'].default_value-.1)<1e-6
    if cfg['label']!='control':
        data=ROOT/cfg['path'];assert sha(data)==cfg['sha256'];field=np.load(data)
        h,w,_=field.shape;im=bpy.data.images.new('Diagnostic polish field',width=w,height=h,alpha=True,float_buffer=True)
        im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(field[::-1].copy().ravel());im.update()
        tex=nodes.new('ShaderNodeTexImage');tex.name='Diagnostic polish texture';tex.image=im
        tex.interpolation='Linear';tex.extension='EXTEND'
        sep=nodes.new('ShaderNodeSeparateColor');sep.mode='RGB'
        uv=nodes['Baked boxwood pigment'].inputs['Vector'].links[0].from_socket
        links.new(uv,tex.inputs['Vector']);links.new(tex.outputs['Color'],sep.inputs['Color'])
        links.new(sep.outputs['Red'],bs.inputs['Roughness']);links.new(sep.outputs['Green'],bs.inputs['Coat Roughness'])
    s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=240/1254;s.render.border_max_x=780/1254
    s.render.border_min_y=1-1170/1254;s.render.border_max_y=1-825/1254
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type=='OPTIX'
    s.cycles.device='GPU' if any(dev.use for dev in prefs.devices) else 'CPU'
    path=out/(cfg['label']+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    records.append(dict(parameters=cfg,render_sha256=sha(path)));print('SPATIAL_POLISH_PROBE',cfg['label'],flush=True)
assert sha(source)==manifest['source_sha256']
report=dict(source=manifest['source'],source_sha256=sha(source),source_unchanged=True,
    fields=a.fields,fields_sha256=sha(ROOT/a.fields),samples=a.samples,crop=[240,825,780,1170],
    fixed_camera=True,diagnostics_only=True,variants=records,
    note='Unsaved local roughness probes. Geometry, color, lights and normal/relief inputs unchanged; these crops are not whole-model candidates.')
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
