"""Validate an isolated declared shape trial without replacing public assets."""
from pathlib import Path
import argparse,json,runpy,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from validate_profile_shape import audit
from bishop_scene import editable_meshes
p=argparse.ArgumentParser();p.add_argument('--config',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
config=ROOT/a.config;cfg=json.loads(config.read_text())
out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
model=out/'bishop.blend';profile=out/'profile.json'
scope=audit(model,config,profile)
(out/'scope-validation.json').write_text(json.dumps(scope,indent=2)+'\n')
path=Path(__file__).with_name('validate.py')
sys.argv=[str(path),'--',str(ROOT),'--model',model.relative_to(ROOT).as_posix(),
          '--profile',profile.relative_to(ROOT).as_posix(),'--out',
          (out/'anatomy-validation.json').relative_to(ROOT).as_posix(),'--skip-export']
runpy.run_path(str(path),run_name='__main__')
graph=bpy.context.evaluated_depsgraph_get();coords=[]
for obj in editable_meshes(bpy.context.scene):
    ev=obj.evaluated_get(graph);mesh=ev.to_mesh()
    coords.extend(tuple(obj.matrix_world@v.co) for v in mesh.vertices)
    ev.to_mesh_clear()
points=np.array(coords);size=np.max(points,axis=0)-np.min(points,axis=0)
report={'passed':True,'source_sha256':scope['source_sha256'],'model_sha256':scope['model_sha256'],
        'config':a.config,'size':size.tolist(),'saved_reopened_scope_and_actual_anatomy_checked':True}
(out/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SHAPE_TRIAL_VALIDATED',json.dumps(report),flush=True)
