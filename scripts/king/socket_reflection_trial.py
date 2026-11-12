"""Split an exact socket receiver and test real, independently routed reflections."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import regenerate,link
from validate_render_regions import check
from base_reflection_trial import main as render_trial


def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    assert s.get('king_render_regions') and s.get('king_split_flare')
    before=check(s);regenerate(s,split_socket=True)
    s['king_socket_broad_excluded']=not cfg.get('preserve_broad_socket',False)
    if s['king_socket_broad_excluded']:
        upper=next(o for o in s.objects if o.get('king_render_region')=='upper-body')
        for name in ('Upper varnish','Front varnish'):link(bpy.data.objects[name],[upper],name+' without socket')
    after=check(s)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    prepared=out/'socket-prepared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prepared))
    render_cfg=dict(cfg)
    render_cfg.update(source=prepared.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(prepared.read_bytes()).hexdigest(),
                      socket_original_source=cfg['source'],socket_original_source_sha256=digest,
                      socket_partition_before=before,socket_partition_after=after)
    render_trial(render_cfg)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
