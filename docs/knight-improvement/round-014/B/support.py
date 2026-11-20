"""Package and optionally replay the six seed files under a clean staging tree."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2]
LOCAL=['map.py','surface.py','donor.py','donor_field.py','restore.py','candidate.py','diagnostics.py','evidence.py','reference_images.py','study.py',
       'qa_geometry.py','verify.py','rear.py','viewer.py','report.py','support.py','reproduce.ps1','REPORT.md']
SEEDS=['parent.blend','parent-pigment.png','parent-wood.png','parent-side.png','arc-samples.json','hollow-samples.json']
EXT=['scripts/knight/'+f for f in ['mission_pose.py','mission_scene.py','lower_carving_fit.py','export_mission.py','validate.py','viewer-template.html',
    'build_viewer.py','check_viewer.cjs','check_native_viewer.cjs']]+['assets/knight/'+f for f in ['ref.png','original.png','original-alignment.json']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rel=D.relative_to(R);paths={str(rel/k):(D/k) for k in [*SEEDS,*LOCAL]};paths.update({e:R/e for e in EXT})
    frozen=json.loads((D/'parameters.json').read_text())
    metadata={'upstream_commit':'a859987','recipe':9,'candidate_directory':rel.as_posix(),
              'local_seed_sha256':{k:sha(D/k) for k in SEEDS},'local_script_and_report_sha256':{k:sha(D/k) for k in LOCAL},
              'staging_helper_and_reference_sha256':{k:sha(R/k) for k in EXT},'expected_pigment_sha256':frozen['pigment_sha256']}
    manifest=D/'support.json';manifest.write_text(json.dumps(metadata,indent=2)+'\n')
    paths[str(rel/'support.json')]=manifest
    bundle=D/'source-and-seeds.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for key,path in sorted(paths.items()):
            entry=zipfile.ZipInfo('stage/'+Path(key).as_posix(),date_time=(2026,11,19,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(entry,path.read_bytes(),compresslevel=3)
    info={'package_sha256':sha(bundle),'bytes':bundle.stat().st_size,'count':len(paths)}
    if '--check-material' in sys.argv:
        check=Path(tempfile.mkdtemp(prefix='replay-',dir=D)).resolve()
        assert check.parent==D.resolve() and check.name.startswith('replay-')
        try:
            with zipfile.ZipFile(bundle) as z:z.extractall(check)
            copy=check/'stage'/rel
            blender=os.environ.get('KNIGHT_BLENDER','C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
            for script,tool,args in [('map.py',blender,[]),('surface.py',sys.executable,[]),('donor.py',blender,[]),
                    ('donor_field.py',sys.executable,[]),('restore.py',sys.executable,['9'])]:
                cmd=[tool,'-B',str(copy/script),*args] if tool==sys.executable else [tool,'-b','--python-exit-code','1','-P',str(copy/script)]
                subprocess.run(cmd,cwd=copy,check=True,capture_output=True)
            current=sha(copy/'atlas-9.png');assert current==metadata['expected_pigment_sha256']
            info['clean_material_replay_sha256']=current
        finally:
            assert check.parent==D.resolve() and check.name.startswith('replay-')
            shutil.rmtree(check)
    (D/'package-proof.json').write_text(json.dumps(info,indent=2)+'\n');print(info,flush=True)
if __name__=='__main__':main()
