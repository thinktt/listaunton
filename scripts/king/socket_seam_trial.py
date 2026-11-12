"""Keep the closed king unchanged and isolate true reflection on its inner fillet."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import regenerate
from validate_render_regions import check
from base_reflection_trial import main as render_trial


def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    before=check(s);assert s.get('king_split_socket');regenerate(s,split_socket_seam=True)
    s['king_socket_seam_lights_confined']=True;after=check(s)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
    prepared=out/'seam-prepared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prepared))
    c=dict(cfg);c.update(source=prepared.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(prepared.read_bytes()).hexdigest(),seam_original_source=cfg['source'],seam_original_source_sha256=digest,seam_partition_before=before,seam_partition_after=after)
    render_trial(c);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
