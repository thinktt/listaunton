"""Split exact flare light receivers without changing the editable king surface."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from render_regions import regenerate,link
from validate_render_regions import check

def main(cfg):
    source=ROOT/cfg['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    regenerate(s,split_flare=True);parts={o['king_render_region']:o for o in s.objects if o.get('king_render_region')}
    link(bpy.data.objects['Base upper focused'],[parts['upper-flare']],'upper flare isolated')
    for ob in s.objects:
        if ob.type=='LIGHT' and ob.name.startswith('Base lower shaped '):link(ob,[parts['lower-flare']],'lower flare isolated '+ob.name)
    check(s);out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=cfg['source_sha256']);run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
