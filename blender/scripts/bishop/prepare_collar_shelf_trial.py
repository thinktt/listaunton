"""Flatten the middle collar's inner deck without sharpening its rolled rim."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
archive=ROOT/'history/bishop-mission-018'
profile=json.loads((archive/'profile.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'build/bishop-mission/150-collar-sections'
assert out.is_dir()
# The compression trials made every outer lip thinner, giving a knife edge.
# Here the full outer roll (rings 51-55) is retained. Only the rising deck
# inside it is lowered into a shallow shelf; the upper collar stays seated.
cfg={'variant':'151-collar-shelf','source':'history/bishop-mission-018/bishop-rebuilt.blend',
     'source_sha256':sha(archive/'bishop-rebuilt.blend'),
     'profile':'history/bishop-mission-018/profile.json','samples':64,
     'body_rings':{str(i):[profile['profile'][i][0],y] for i,y in
                   [(56,99.94),(57,99.90),(58,99.30)]},
     'interpretation':'Unaccepted inner-deck-only geometry hypothesis. Lower the rising middle-collar deck into a shallower shelf while retaining its complete rounded outer lip and both neighbouring collars. No camera, reference, UV, pigment or lighting change.'}
(out/'shelf.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared inner shelf trial; no public model changed.')
