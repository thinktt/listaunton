"""Isolate existing collar illumination and relief in unsaved fixed-view crops."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from bishop_scene import editable_meshes
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',default='history/bishop-mission-013/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/107-collar-isolation');p.add_argument('--samples',type=int,default=128)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/a.source;out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=sha(source)
variants=[('control',{},None),('without-collar',{'collars reflection':0},None),
 ('without-head',{'head reflection':0},None),('without-both',{'head reflection':0,'collars reflection':0},None),
 ('without-relief',{},0),('double-collar',{'collars reflection':2},None)]
records=[];box=[290,405,690,630]
for name,powers,relief in variants:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    original=[]
    for light,factor in powers.items():
        ob=bpy.data.objects[light];assert ob.visible_glossy and not ob.visible_diffuse
        original.append({'light':light,'before':ob.data.energy,'factor':factor});ob.data.energy*=factor
    if relief is not None:
        mat=editable_meshes(s)[0].data.materials[0]
        mat.node_tree.nodes['Wood micro relief'].inputs['Strength'].default_value=relief
    w,h=s.render.resolution_x,s.render.resolution_y;s.render.resolution_percentage=100
    s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=box[0]/w;s.render.border_max_x=box[2]/w
    s.render.border_min_y=1-box[3]/h;s.render.border_max_y=1-box[1]/h
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'label':name,'light_changes':original,'main_bump_strength':relief,'render_sha256':sha(out/(name+'.png'))})
    print('COLLAR_PROBE_COMPLETE',name,flush=True)
assert sha(source)==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'crop':box,'samples':a.samples,'camera_unchanged':True,'variants':records,
 'note':'Unsaved actual-BSDF crops for diagnosis only. Source geometry, materials and lights are not saved or promoted.'},indent=2)+'\n')
