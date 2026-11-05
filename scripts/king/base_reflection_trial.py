"""Real BSDF trials with independently lit foot/flare receivers."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls,partition,link
from focused_reflections import target

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    objects=controls(s);assert len(objects)==2;body=next(o for o in objects if 'body' in o.name)
    if not s.get('king_render_regions'):parts,report=partition(s,body,profile_sections=cfg.get("profile_sections",False))
    else:parts=[o for o in s.objects if o.get('king_render_region')];report=[]
    by_name={o['king_render_region']:o for o in parts}
    if cfg.get('confine_existing'):
        for name in ['Upper varnish','Front varnish']:link(bpy.data.objects[name],[by_name['upper-body']],name+' upper-body only')
    for name,power in cfg.get('existing_light_power',{}).items():bpy.data.objects[name].data.energy=power
    probes=[]
    for row in cfg.get('reflectors',[]):
        ob,point,direction,normal=target(s,*row['pixel']);position=point+direction*row.get('distance',6)
        data=bpy.data.lights.new(row['name'],'SPOT');data.energy=row['energy'];data.color=row.get('color',[1,.84,.70]);data.shadow_soft_size=row.get('radius',.5);data.spot_size=math.radians(row.get('degrees',8));data.spot_blend=.9
        light=bpy.data.objects.new(row['name'],data);s.collection.objects.link(light);light.location=position;light.rotation_euler=(point-position).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True
        link(light,[by_name[name] for name in row.get('receivers',[ob.get('king_render_region')])],row['name'])
        probes.append(dict(row,receiver_hit=ob.name,point=list(point),normal=list(normal),position=list(position)))
    axis=s.camera.matrix_world.to_3x3()@Vector((0,0,1));elevation=math.degrees(math.asin(axis.z));assert s.camera.data.type=='ORTHO' and abs(elevation-54)<.001
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);gpu(s);s.render.engine='CYCLES';s.cycles.samples=cfg.get('samples',96);s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
    cfg.update(original_source_sha256=digest,receiver_partitions=report,reflector_probes=probes,elevation_degrees=elevation)
    s['king_mission_variant']=cfg['variant'];s['king_mission_config']=json.dumps(cfg,sort_keys=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'king.blend'));bpy.ops.render.render(write_still=True)
    cfg['model_sha256']=hashlib.sha256((out/'king.blend').read_bytes()).hexdigest();(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('KING_BASE_REFLECTION_TRIAL_DONE',cfg['variant'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
