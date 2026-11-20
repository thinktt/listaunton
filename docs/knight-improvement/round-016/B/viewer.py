"""Prepare the actual offline viewer with the two real, registered side renders."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=D/'review-copy';a=root/'assets/knight';scripts=root/'scripts/knight';scripts.mkdir(parents=True,exist_ok=True)
    for name in ['build_viewer.py','viewer-template.html','check_viewer.cjs','check_native_viewer.cjs']:
        shutil.copyfile(R/'scripts/knight'/name,scripts/name)
    for name in ['ref.png','original.png','original-alignment.json']:
        shutil.copyfile(R/'assets/knight'/name,a/name)
    for src,dst in [('wood.png','render.png'),('wood-side.png','guide-render.png'),('parent-side.png','parent-side.png')]:
        shutil.copyfile(D/src,a/dst)
    config={'guide':'assets/knight/parent-side.png','profile':'assets/knight/guide-render.png',
        'source_blend_sha256':sha(D/'knight.blend'),'guide_sha256':sha(a/'parent-side.png'),
        'profile_sha256':sha(a/'guide-render.png'),'profile_size':[1254,1254],
        'canvas':[1254,1254],'guide_top':0,'scale':1,'offset_x':0,'offset_y':0,
        'physical_foot_center_x':.03251595380318414,
        'method':'The private review overlays the actual 15A and 16B renders in their shared registered side camera.'}
    (a/'side-registration.json').write_text(json.dumps(config,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(scripts/'build_viewer.py')],check=True)
if __name__=='__main__':main()
