"""Archive the exact seeds and helpers for reproduction from a private mission tree."""
from pathlib import Path
import hashlib,json,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2]
SCRIPTS=['carve.py','seat.py','orbital.py','survey.py','lamp_probe.py','finish_probe.py','mesh_check.py','verify.py','replay.py','eye_portraits.py','evidence.py','diagnostics.py',
         'eye_study.py','reference_images.py','study.py','sweep.py','moving.py','common_fixed.py','bilateral_eye.py','plot_bilateral_eye.py',
         'socket_sections.py','viewer.py','report.py','support.py','reproduce.ps1','REPORT.md']
SEEDS=['parent.blend','parent-wood.png','parent-side.png','pigment.png','recipe.json','upper-source.json','lower-trace.json','inner-source.json']
EXT=['scripts/knight/'+s for s in ['mission_scene.py','mission_pose.py','lower_carving_fit.py','probe_carving.py','export_mission.py','validate.py',
      'viewer-template.html','build_viewer.py','check_viewer.cjs','check_native_viewer.cjs']]+['assets/knight/'+s for s in ['ref.png','original.png','original-alignment.json']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rel=D.relative_to(R);manifest={'upstream_commit':'108b391','recipe':json.loads((D/'recipe.json').read_text())['design'],'candidate_directory':rel.as_posix(),
        'local_seed_sha256':{s:sha(D/s) for s in SEEDS},'local_script_and_report_sha256':{s:sha(D/s) for s in SCRIPTS},
        'staging_helper_and_reference_sha256':{s:sha(R/s) for s in EXT},'expected_pigment_sha256':sha(D/'pigment.png')}
    (D/'support.json').write_text(json.dumps(manifest,indent=2)+'\n')
    paths=[*(D/s for s in SEEDS+SCRIPTS+['support.json']),*(R/s for s in EXT)]
    dest=D/'source-and-seeds.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for path in paths:z.write(path,'stage/'+path.relative_to(R).as_posix())
    with zipfile.ZipFile(dest) as z:
        for path in paths:assert hashlib.sha256(z.read('stage/'+path.relative_to(R).as_posix())).hexdigest()==sha(path)
    proof={'package_sha256':sha(dest),'bytes':dest.stat().st_size,'verified_files':len(paths)}
    (D/'package-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)
if __name__=='__main__':main()
