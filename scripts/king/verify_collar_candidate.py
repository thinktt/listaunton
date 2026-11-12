"""Validate and independently reproduce a collar candidate before publication.

Run with ordinary Python and an installed Blender executable. Never replaces the
accepted model. Fixed beauty uses the documented canonical fresh-render entrypoint.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def difference(a,b):
    a,b=[np.asarray(Image.open(p).convert('RGBA'),dtype=np.int16) for p in (a,b)]
    return dict(maximum_channel_error_255=int(abs(a-b).max()),mean_channel_error_255=float(abs(a-b).mean()),alpha_exact=bool(np.array_equal(a[:,:,3],b[:,:,3])))

def main(args):
    out=ROOT/args.output;logs=out/'checks';logs.mkdir(parents=True,exist_ok=True)
    candidate=ROOT/'build/king-mission'/args.variant
    source=candidate/'king.blend';baseline=ROOT/args.baseline
    before=[sha(p) for p in (source,baseline)]
    cfg=read(candidate/'input.json')
    assert cfg['source_sha256']==sha(baseline)
    assert all(p['clear_path'] for p in read(candidate/'turning.json')['probes'])
    write(out/'accepted-input.json',dict(cfg,source=args.baseline))
    reproduction=dict(cfg,source=args.baseline,variant=args.reproduction)
    write(out/'reproduction.json',reproduction)
    independent=ROOT/'build/king-mission'/args.reproduction
    def relative(path):return path.relative_to(ROOT).as_posix()
    def run(name,script,parameters):
        print('Running '+name,flush=True)
        with (logs/(name+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run([args.blender,'--background','--python-exit-code','1','--python',str(ROOT/'scripts/king'/script),'--',*parameters],stdout=log,stderr=subprocess.STDOUT,check=True)
        print('Passed '+name,flush=True)
    run('scope','check_collar_turning.py',[args.baseline,relative(source),relative(out/'accepted-input.json'),relative(out/'scope-check.json')])
    run('regeneration','check_region_regeneration.py',[relative(source),relative(out/'regeneration-check.json')])
    run('export','export_mission.py',[relative(source),relative(candidate)])
    run('saved-diagnostics','render_fixed_diagnostics.py',[relative(source),relative(candidate)])
    inspections=candidate/'inspections'
    run('side-rear','render_inspections.py',[relative(source),relative(inspections)])
    for name in ('side.png','rear.png'):shutil.copy2(inspections/name,candidate/name)
    run('repeat-fixed','render_fixed_diagnostics.py',[relative(source),relative(candidate/'repeat'),'--beauty-only'])
    run('reproduce','refine_collar_turning.py',[str(out/'reproduction.json')])
    run('reproduction-fresh','render_fixed_diagnostics.py',[relative(independent/'king.blend'),relative(independent),'--beauty-only'])
    run('reproduction-export','export_mission.py',[relative(independent/'king.blend'),relative(independent)])
    write(out/'identity-config.json',dict(profile_offsets={},reaim=[],samples=128))
    run('independent-scene-identity','check_collar_turning.py',[relative(source),relative(independent/'king.blend'),relative(out/'identity-config.json'),relative(out/'independent-scope.json')])
    checks=dict(initial_session_vs_fresh=difference(candidate/'wood.png',candidate/'wood-reopened.png'),
        independent_saved_reproduction=difference(candidate/'wood-reopened.png',independent/'wood-reopened.png'),
        repeat_saved_render=difference(candidate/'wood-reopened.png',candidate/'repeat/wood-reopened.png'),
        alternate_entrypoint=difference(candidate/'wood-reopened.png',inspections/'wood-reopened.png'),
        reproduction_mesh_exact=sha(candidate/'mesh.bin')==sha(independent/'mesh.bin'),
        camera_export_exact=sha(candidate/'camera.json')==sha(baseline.parent/'camera.json'),
        physical_bounds_exact=read(candidate/'mesh.json')['bounds']==read(baseline.parent/'mesh.json')['bounds'],
        canonical_render_entrypoint='scripts/king/render_fixed_diagnostics.py -- SOURCE OUTPUT --beauty-only')
    write(out/'reproduction-checks.json',checks)
    for name in ('independent_saved_reproduction','repeat_saved_render'):
        assert checks[name]['maximum_channel_error_255']<=1 and checks[name]['alpha_exact'],(name,checks[name])
    assert all(checks[k] for k in ('reproduction_mesh_exact','camera_export_exact','physical_bounds_exact'))
    assert [sha(p) for p in (source,baseline)]==before
    print('COLLAR_CANDIDATE_VALIDATION_PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('baseline');p.add_argument('output');p.add_argument('reproduction');p.add_argument('--blender',default='blender')
    main(p.parse_args())
