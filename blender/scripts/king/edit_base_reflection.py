"""Edit declared existing base spotlights while preserving the accepted king."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from focused_reflections import target
from render_regions import clear_light_path

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;assert not s.cycles.use_light_tree
    probes=[]
    for row in cfg['edits']:
        ob=bpy.data.objects[row['name']];assert row['name'].startswith('Base ') and ob.data.type=='SPOT'
        assert set(row).issubset({'name','degrees','radius','energy','pixel','distance','receiver'})
        if 'pixel' in row:
            surface,p,d,n=target(s,*row['pixel']);distance=row['distance'];assert surface.get('king_render_region')==row['receiver']
            assert clear_light_path(s,p,n,d,distance)
            ob.location=p+d*distance;ob.rotation_euler=(p-ob.location).to_track_quat('-Z','Y').to_euler()
            probes.append(dict(light=row['name'],pixel=row['pixel'],receiver=surface.get('king_render_region'),point=list(p),normal=list(n),reflection=list(d),clear_path=True))
        if 'degrees' in row:ob.data.spot_size=math.radians(row['degrees'])
        if 'radius' in row:ob.data.shadow_soft_size=row['radius']
        if 'energy' in row:ob.data.energy=row['energy']
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    (out/'reflection-probes.json').write_text(json.dumps(probes,indent=2)+'\n',encoding='utf-8')
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    run(dict(cfg,source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
