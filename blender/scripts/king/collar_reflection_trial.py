"""Partition exact king collar surfaces before adding local real reflectors."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import regenerate, COLLAR_RANGES, link
from validate_render_regions import check
from base_reflection_trial import main as render_trial
from focused_reflections import target


def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    before=check(s);regenerate(s,split_collars=True);preserved=check(s)
    if cfg.get('exclude_broad',True):
        for name in ['Upper varnish','Front varnish']:
            light=bpy.data.objects[name]
            kept=[o for o in light.light_linking.receiver_collection.objects if o.get('king_render_region') not in COLLAR_RANGES]
            assert kept;link(light,kept,name+' without collars')
        s['king_collar_broad_excluded']=True
    after=check(s)
    for row in cfg.get('reflectors',[]):
        hit,_,_,_=target(s,*row['pixel'])
        assert hit.get('king_render_region') in row['receivers'],(row['name'],row['pixel'],hit.get('king_render_region'))
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    prepared=out/'collars-prepared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prepared))
    c=dict(cfg);c.update(source=prepared.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(prepared.read_bytes()).hexdigest(),
        collar_original_source=cfg['source'],collar_original_source_sha256=digest,collar_partition_before=before,
        collar_preserved_partition=preserved,collar_partition_after=after,collar_intervals=COLLAR_RANGES)
    render_trial(c);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
