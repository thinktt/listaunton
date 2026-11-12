"""Reopen, inspect, export and independently reproduce a bounded king finish."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_collar_candidate import difference
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main(args):
    out=ROOT/args.output;logs=out/'checks';logs.mkdir(parents=True,exist_ok=True)
    candidate=ROOT/'build/king-mission'/args.variant;source=candidate/'king.blend';baseline=ROOT/args.baseline
    digests=[sha(p) for p in (source,baseline)];cfg=read(candidate/'input.json')
    assert cfg['source_sha256']==digests[1]
    write(out/'accepted-input.json',dict(cfg,source=args.baseline))
    write(out/'reproduction.json',dict(cfg,source=args.baseline,variant=args.reproduction))
    independent=ROOT/'build/king-mission'/args.reproduction
    def rel(p):return p.relative_to(ROOT).as_posix()
    def run(name,script,parameters):
        print('Running '+name,flush=True)
        with (logs/(name+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run([args.blender,'--background','--python-exit-code','1','--python',str(ROOT/'scripts/king'/script),'--',*parameters],stdout=log,stderr=subprocess.STDOUT,check=True)
        print('Passed '+name,flush=True)
    run('scope','check_local_finish.py',[args.baseline,rel(source),rel(out/'accepted-input.json'),rel(out/'scope-check.json')])
    run('regeneration','check_region_regeneration.py',[rel(source),rel(out/'regeneration-check.json')])
    run('export','export_mission.py',[rel(source),rel(candidate)])
    run('saved-diagnostics','render_fixed_diagnostics.py',[rel(source),rel(candidate)])
    inspections=candidate/'inspections'
    run('side-rear','render_inspections.py',[rel(source),rel(inspections)])
    for name in ('side.png','rear.png'):shutil.copy2(inspections/name,candidate/name)
    run('repeat-fixed','render_fixed_diagnostics.py',[rel(source),rel(candidate/'repeat'),'--beauty-only'])
    run('reproduce','local_finish_trial.py',[str(out/'reproduction.json')])
    run('reproduction-fresh','render_fixed_diagnostics.py',[rel(independent/'king.blend'),rel(independent),'--beauty-only'])
    run('reproduction-export','export_mission.py',[rel(independent/'king.blend'),rel(independent)])
    run('independent-scene-identity','check_local_finish.py',[rel(source),rel(independent/'king.blend'),rel(out/'accepted-input.json'),rel(out/'independent-scope.json'),'--identity'])
    checks=dict(initial_session_vs_fresh=difference(candidate/'wood.png',candidate/'wood-reopened.png'),
        independent_saved_reproduction=difference(candidate/'wood-reopened.png',independent/'wood-reopened.png'),
        repeat_saved_render=difference(candidate/'wood-reopened.png',candidate/'repeat/wood-reopened.png'),
        alternate_entrypoint=difference(candidate/'wood-reopened.png',inspections/'wood-reopened.png'),
        reproduction_mesh_exact=sha(candidate/'mesh.bin')==sha(independent/'mesh.bin'),
        baseline_mesh_exact=sha(candidate/'mesh.bin')==sha(baseline.parent/'mesh.bin'),
        camera_export_exact=sha(candidate/'camera.json')==sha(baseline.parent/'camera.json'),
        physical_bounds_exact=read(candidate/'mesh.json')['bounds']==read(baseline.parent/'mesh.json')['bounds'],
        canonical_render_entrypoint='scripts/king/render_fixed_diagnostics.py -- SOURCE OUTPUT --beauty-only')
    write(out/'reproduction-checks.json',checks)
    for name in ('independent_saved_reproduction','repeat_saved_render'):
        assert checks[name]['maximum_channel_error_255']<=1 and checks[name]['alpha_exact'],(name,checks[name])
    assert all(checks[k] for k in ('reproduction_mesh_exact','baseline_mesh_exact','camera_export_exact','physical_bounds_exact'))
    assert [sha(p) for p in (source,baseline)]==digests
    print('KING_FINISH_CANDIDATE_VALIDATION_PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('baseline');p.add_argument('output');p.add_argument('reproduction');p.add_argument('--blender',default='blender')
    main(p.parse_args())
