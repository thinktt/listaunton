"""Render both frozen pieces with the unaltered physical lights from the parent."""
from pathlib import Path
import sys,json
import numpy as np
import bpy
from mathutils import Matrix
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import configure_render,render,use_side_camera,sha
parent=D/'parent.blend';candidate=D/'knight.blend'
bpy.ops.wm.open_mainfile(filepath=str(parent),load_ui=False);s=bpy.context.scene
rig={ob.name:[np.asarray(ob.matrix_world).tolist(),ob.data.color[:],ob.data.energy,ob.data.shape,ob.data.size,ob.data.size_y,ob.data.spread] for ob in s.objects if ob.type=='LIGHT'}
bpy.ops.wm.open_mainfile(filepath=str(candidate),load_ui=False);s=bpy.context.scene
for name,(matrix,color,power,shape,dx,dy,spread) in rig.items():
    ob=s.objects[name];ob.matrix_world=Matrix(matrix);l=ob.data
    l.color=color;l.energy=power;l.shape=shape;l.size=dx;l.size_y=dy;l.spread=spread
bpy.context.view_layer.update();configure_render(s,144)
for key in ('fixed','side'):
    if key=='side':use_side_camera(s)
    render(s,D/('matched-parent-'+key+'.png'))
(D/'matched-studio.json').write_text(json.dumps({'model':sha(candidate),'parent_lights':sha(parent),'samples':144,'renders':{k:sha(D/('matched-parent-'+k+'.png')) for k in ('fixed','side')}},indent=2)+'\n')
