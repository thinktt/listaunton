"""Small explicit collar profile edits, with optional existing-light re-aiming."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy, numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from render_regions import controls,regenerate,clear_light_path
from focused_reflections import target
from validate_render_regions import check

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    body=next(o for o in controls(s) if 'body' in o.name)
    co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    for index,(dr,dz) in cfg['profile_offsets'].items():
        j=int(index);assert 34<=j<=61
        r=np.linalg.norm(co[j,:,:2],axis=1)
        co[j,:,:2]*=((r+dr)/r)[:,None];co[j,:,2]+=dz
    body.data.vertices.foreach_set('co',co.reshape(-1));body.data.update();regenerate(s)
    probes=[]
    for row in cfg.get('reaim',[]):
        light=bpy.data.objects[row['name']]
        hit,point,direction,normal=target(s,*row['pixel'])
        assert hit.get('king_render_region')==row['receiver']
        position=point+direction*row['distance']
        light.location=position;light.rotation_euler=(point-position).to_track_quat('-Z','Y').to_euler()
        if 'energy' in row:light.data.energy=row['energy']
        for key in ('size','size_y'):
            if key in row:
                assert light.data.type=='AREA';setattr(light.data,key,row[key])
        probes.append(dict(name=row['name'],pixel=row['pixel'],point=list(point),normal=list(normal),position=list(position),
                           clear_path=clear_light_path(s,point,normal,direction,row['distance'])))
    if 'adaptive_sampling' in cfg:s.cycles.use_adaptive_sampling=cfg['adaptive_sampling']
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    report=dict(source_sha256=digest,profile_offsets=cfg['profile_offsets'],probes=probes,receivers=check(s),
                render_sampling=dict(samples=cfg.get('samples',128),adaptive=s.cycles.use_adaptive_sampling,denoising=True))
    (out/'turning.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('TURNING_PROBES',json.dumps(probes),flush=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='profile_offsets'}
    rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),
                     original_source=cfg['source'],original_source_sha256=digest,turning=report)
    run(rendercfg);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
