"""Preserve checkpoint 018 and propose thinner plate cross-sections.

This is a geometry hypothesis prompted by the owner's blink comparison.
Radius crests and camera remain fixed. No texture, source transform or
silhouette score is used to conceal an internal-form mismatch.
"""
from pathlib import Path
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archive=ROOT/'history/bishop-mission-018'
archive.mkdir(exist_ok=True)
files=[('models/bishop/bishop-rebuilt.blend','bishop-rebuilt.blend'),
       ('scripts/bishop/profile.json','profile.json')]+[
       ('assets/bishop/'+name,name) for name in
       ['render.png','render-clay.png','side-profile.png','head-side.png',
        'rear-oblique.png','camera.json','mesh.json','mesh.bin','bishop-boxwood-albedo.png']]
for original,name in files:
    src=ROOT/original;dest=archive/name
    if dest.exists():assert sha(src)==sha(dest),name
    else:shutil.copy2(src,dest)
profile=json.loads((archive/'profile.json').read_text())
out=ROOT/'build/bishop-mission/150-collar-sections'
out.mkdir(exist_ok=True)
# Each lobe's maximum radius ring anchors its physical crest. Compress the
# nearby upper/lower roll, smoothly tapering to unchanged joins. These are
# proposals, not measured reference cross-sections or accepted geometry.
lobes=[{'name':'upper','crest':62,'weights':{59:.25,60:.65,61:1,62:1,63:1,64:.5}},
       {'name':'middle','crest':53,'weights':{50:.3,51:.75,52:1,53:1,54:1,55:.7,56:.3}},
       {'name':'lower','crest':44,'weights':{41:.25,42:.65,43:1,44:1,45:1,46:.9,47:.65,48:.25}}]
for label,amount in [('moderate',.35),('flatter',.6)]:
    rings={}
    for lobe in lobes:
        center=profile['profile'][lobe['crest']][1]
        for i,w in lobe['weights'].items():
            radius,y=profile['profile'][i]
            new_y=y+(center-y)*amount*w
            if abs(new_y-y)>1e-10:rings[str(i)]=[radius,new_y]
    cfg={'variant':'150-collars-'+label,'source':'history/bishop-mission-018/bishop-rebuilt.blend',
         'source_sha256':sha(archive/'bishop-rebuilt.blend'),
         'profile':'history/bishop-mission-018/profile.json','samples':64,
         'body_rings':rings,'interpretation':
         'Unaccepted plate-section hypothesis: compress collar roll heights around unchanged maximum-radius crests; preserve head, button, slit, stem, socket, base, total bounds, UVs, pigment, lights and fixed camera.',
         'section_compression':amount,'lobes':lobes}
    (out/(label+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared two unaccepted collar cross-section trials from preserved 018.')
