"""Render neutral before/after views from saved files without changing either."""
from pathlib import Path
import json,runpy,sys
ROOT=Path(__file__).resolve().parents[2]
cfg=json.loads((ROOT/'docs/bishop-mission/iteration-030/family-style.json').read_text())
jobs=[('before',cfg['source']),('after','build/bishop-mission/'+cfg['variant']+'/bishop.blend')]
if '--after-only' in sys.argv:jobs=jobs[1:]
for key,source in jobs:
    script=Path(__file__).with_name('render_geometry_studio.py')
    sys.argv=[str(script),'--','--source',source,'--out',f'docs/bishop-mission/iteration-030/{key}','--views','side','fixed']
    runpy.run_path(str(script),run_name='__main__')
print('FAMILY_GEOMETRY_EVIDENCE_COMPLETE',flush=True)
