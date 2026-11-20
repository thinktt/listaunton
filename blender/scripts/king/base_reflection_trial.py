"""Real BSDF trials with independently lit foot/flare receivers."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls,partition,link,clear_light_path
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
    for name,changes in cfg.get('existing_light_edits',{}).items():
        data=bpy.data.objects[name].data;assert data.type=='SPOT' and set(changes)=={'degrees'};data.spot_size=math.radians(changes['degrees'])
    probes=[]
    for row in cfg.get('reflectors',[]):
        actual_pixel=list(row['pixel'])
        for shift in range(row.get('seek_receiver_down',0)+1):
            actual_pixel=[row['pixel'][0],row['pixel'][1]+shift]
            ob,point,direction,normal=target(s,*actual_pixel)
            unobstructed=(not row.get('require_clear_path')) or clear_light_path(s,point,normal,direction,row.get('distance',6))
            if not row.get('seek_receiver_down') or (ob.get('king_render_region') in row['receivers'] and normal.z>=row.get('minimum_normal_z',0) and unobstructed):break
        if row.get('seek_receiver_down'):assert ob.get('king_render_region') in row['receivers'] and normal.z>=row.get('minimum_normal_z',0) and unobstructed,(row,actual_pixel,ob.name,normal[:])
        position=point+direction*row.get('distance',6)
        kind=row.get('type','SPOT');data=bpy.data.lights.new(row['name'],kind);data.energy=row['energy'];data.color=row.get('color',[1,.84,.70])
        if kind=='SPOT':
            data.shadow_soft_size=row.get('radius',.5);data.spot_size=math.radians(row.get('degrees',8));data.spot_blend=.9
        elif kind=='AREA':
            data.shape=row.get('shape','RECTANGLE');data.size=row['size']
            if data.shape=='RECTANGLE':data.size_y=row['size_y']
        else:raise ValueError('Unsupported reflector '+kind)
        light=bpy.data.objects.new(row['name'],data);s.collection.objects.link(light);light.location=position;light.rotation_euler=(point-position).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True
        link(light,[by_name[name] for name in row.get('receivers',[ob.get('king_render_region')])],row['name'])
        probes.append(dict(row,actual_target_pixel=actual_pixel,receiver_hit=ob.name,point=list(point),normal=list(normal),position=list(position)))
    axis=s.camera.matrix_world.to_3x3()@Vector((0,0,1));elevation=math.degrees(math.asin(axis.z));assert s.camera.data.type=='ORTHO' and abs(elevation-54)<.001
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);gpu(s);s.render.engine='CYCLES';s.cycles.samples=cfg.get('samples',96);s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
    cfg.update(original_source_sha256=digest,receiver_partitions=report,reflector_probes=probes,elevation_degrees=elevation)
    s['king_mission_variant']=cfg['variant'];s['king_mission_config']=json.dumps(cfg,sort_keys=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'king.blend'));bpy.ops.render.render(write_still=True)
    cfg['model_sha256']=hashlib.sha256((out/'king.blend').read_bytes()).hexdigest();(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('KING_BASE_REFLECTION_TRIAL_DONE',cfg['variant'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
