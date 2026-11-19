"""Extract the real lathe controls of the king, queen and restored bishop."""
from pathlib import Path
import hashlib,json,sys,subprocess
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'build/bishop-mission/186-style-sources'
DOC=ROOT/'docs/bishop-mission/iteration-030'
BODY={'king':'King - continuous turned body','queen':'01 Queen - continuous body','bishop':'Bishop - continuous turned body'}
N={'king':96,'queen':192,'bishop':128}
sources_path=SOURCES/'sources.json'
if sources_path.exists():
    sources=json.loads(sources_path.read_text())
else:
    sources={p:{k:row[k] for k in ['file','sha256','copied','git_commit']}
             for p,row in json.loads((DOC/'style-sources.json').read_text()).items()}
result={}
for piece in ('king','queen','bishop'):
    file=SOURCES/(piece+'.blend')
    if not file.is_file():
        file.parent.mkdir(parents=True,exist_ok=True)
        content=subprocess.check_output(['git','show',sources[piece]['git_commit']+':'+sources[piece]['file']],cwd=ROOT)
        assert hashlib.sha256(content).hexdigest()==sources[piece]['sha256']
        file.write_bytes(content)
    assert hashlib.sha256(file.read_bytes()).hexdigest()==sources[piece]['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False)
    scene=bpy.context.scene
    obj,=[o for o in scene.objects if o.name.startswith(BODY[piece])]
    # The king carries a small authored roll on its object. Read its lathe
    # in local coordinates so the turning can be compared on its own axis.
    verts=np.asarray([list(v.co) for v in obj.data.vertices])
    controls=verts.reshape(-1,N[piece],3)
    radius=np.linalg.norm(controls[:,:,:2],axis=2).mean(axis=1)
    z=controls[:,:,2].mean(axis=1)
    turned_count=80 if piece=='queen' else len(z)
    assert np.max(abs(controls[:turned_count,:,2]-z[:turned_count,None]))<1e-5
    assert np.max(abs(np.linalg.norm(controls[:turned_count,:,:2],axis=2)-radius[:turned_count,None]))<1e-5
    for modifier in obj.modifiers:
        if modifier.type=='SUBSURF':modifier.levels=modifier.render_levels
    bpy.context.view_layer.update()
    tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
    levels=np.arange(.001,4.80,.001)
    curve=[]
    for height in levels:
        point,_,_,_=tree.ray_cast(Vector((-3,0,float(height))),Vector((1,0,0)),6)
        if point is not None:curve.append([-float(point.x),float(height)])
    result[piece]={**sources[piece],'segments':N[piece],'object':obj.name,
                   'object_to_world':[list(row) for row in obj.matrix_world],
                   'control_rz':np.column_stack((radius,z)).tolist(),'evaluated_rz':curve,
                   'foot_diameter':2*max(r for r,z in curve if z<.35)}
    print(piece,'rings',len(radius),'base diameter',result[piece]['foot_diameter'],flush=True)
DOC.mkdir(exist_ok=True,parents=True)
(DOC/'style-sources.json').write_text(json.dumps(result,indent=2)+'\n')
