"""Run the unmodified mission exporter to this trial's own directories and compare buffers."""
import sys,json,hashlib
from pathlib import Path
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'scripts/knight'))
from export_mission import export
from mission_scene import sha
out={}
for scene_name,tex,folder in [('parent','parent-pigment.png','export-parent'),('knight','pigment.png','web-export')]:
    source=D/(scene_name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    dest=D/folder;dest.mkdir(exist_ok=True)
    meta=export(bpy.context.scene,D/tex,output=dest,source=source)
    out[scene_name]={k:meta[k] for k in ['vertexCount','indexCount','triangleCount','textureSha256','sourceSha256']}
    out[scene_name]['buffers']={name:sha(dest/name) for name in ['mesh.bin','varnish.bin','camera.json']}
assert out['knight']['buffers']==out['parent']['buffers']
(D/'export-check.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
