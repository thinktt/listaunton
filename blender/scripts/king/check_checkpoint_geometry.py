"""Check material-only trials preserve the editable king controls and camera."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
def read(path):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/path),load_ui=False);s=bpy.context.scene;objects={}
    from render_regions import controls
    for ob in controls(s):
        co=np.array([v.co[:] for v in ob.data.vertices],dtype='<f4');faces=[list(f.vertices) for f in ob.data.polygons]
        objects[ob.name]={'positions_sha256':hashlib.sha256(co.tobytes()).hexdigest(),'faces_sha256':hashlib.sha256(json.dumps(faces).encode()).hexdigest(),'matrix':list(v for row in ob.matrix_world for v in row),'modifiers':[(m.type,m.levels,m.render_levels) for m in ob.modifiers if m.type=='SUBSURF']}
    cam=s.camera
    return {'objects':objects,'camera_matrix':list(v for row in cam.matrix_world for v in row),'camera_type':cam.data.type,'camera_scale':cam.data.ortho_scale,'camera_shift':[cam.data.shift_x,cam.data.shift_y]}
before=read(a.before);after=read(a.after);assert before==after,'Editable geometry or camera changed'
report={'editable_geometry_and_camera_exactly_preserved':True,'before':a.before,'after':a.after,'geometry':after,'note':'Evaluated subdivision may differ by floating-point roundoff after UV-layer changes; compare exported triangle corners separately.'}
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_CONTROLS_AND_CAMERA_UNCHANGED')
