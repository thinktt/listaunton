"""Sculpt the shared crown in rest space and render the reopened candidate."""
from pathlib import Path
import json,sys
import bpy
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from shape import offsets
from ear_tip import ear_displacement
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,save_model,sha,world_vertices
from diagnostic_views import pictures

PARENT='1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208'
SCULPTED=['swept rounded mane','near swept ear','far swept ear','continuous horse head and neck',
          'coherent skull cheek and conical muzzle','curved neck and chest']

def carve(obj,pose,q):
    world=world_vertices(obj);rest=rest_coords(world,pose)
    diff=ear_displacement(rest,q) if obj.name.endswith('swept ear') else offsets(rest,q)
    steps=posed(rest+diff,*pose)-posed(rest,*pose)
    steps[~np.any(diff,axis=1)]=0
    # Apply increments to the original local coordinates. Points outside the
    # sculpted volume therefore keep their exact binary positions.
    mesh=obj.data;positions=np.empty((len(mesh.vertices),3),np.float32)
    mesh.vertices.foreach_get('co',positions.ravel())
    moved=positions+(steps@np.linalg.inv(np.array(obj.matrix_world)[:3,:3]).T)
    mesh.vertices.foreach_set('co',moved.astype(np.float32).ravel());mesh.update()
    length=np.linalg.norm(diff,axis=1)
    return {'changed_vertices':int((length>1e-6).sum()),'max_shift':float(length.max()),
            'max_vertical_shift':float(np.abs(diff[:,2]).max()),
            'vertices_below_z_4_20_moved':int(np.count_nonzero((rest[:,2]<4.2)&(length>1e-6)))}

def build():
    fit=json.loads((D/'fit.json').read_text())
    assert sha(D/'parent.blend')==PARENT==fit['parent_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
    scene=bpy.context.scene;p=json.loads(scene['knight_mission_pose'])
    pose=[p[k] for k in ('dx','dy','twist_degrees')]
    cfg={'parent_sha256':PARENT,'pose':pose,'parameters':dict(zip(fit['parameter_names'],fit['q'])),'geometry':{},
         'ear_tip':{'recovery_fraction':.89,'outward_turn':.036,'rise_to_width_ratio':1.37,
                    'weight_extent_rest_x':[-.93,-.20]}}
    for suffix in SCULPTED:
        obj=bpy.data.objects['Knight | '+suffix];cfg['geometry'][obj.name]=carve(obj,pose,fit['q'])
    scene['knight_improvement_007_A']=json.dumps(cfg)
    configure_render(scene,144);save_model(scene,D/'knight.blend')
    cfg['model_sha256']=sha(D/'knight.blend');json_file(D/'parameters.json',cfg)
    print('ROUND_7A_SCULPT',cfg['model_sha256'],cfg['parameters'],flush=True)

if __name__=='__main__':
    if '--render-only' not in sys.argv:build()
    if '--build-only' not in sys.argv:pictures()
