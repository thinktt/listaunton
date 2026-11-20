"""Prove checkpoint004 changes only the five intended foot profile heights."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls

def read(path):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/path),load_ui=False);s=bpy.context.scene
    objects={o.name:dict(co=np.array([v.co[:] for v in o.data.vertices]),faces=[list(p.vertices) for p in o.data.polygons],matrix=[v for row in o.matrix_world for v in row],uv=np.array([v.uv[:] for v in o.data.uv_layers['Pigment atlas'].data])) for o in controls(s)}
    camera=dict(matrix=[v for row in s.camera.matrix_world for v in row],scale=s.camera.data.ortho_scale,shift=[s.camera.data.shift_x,s.camera.data.shift_y],kind=s.camera.data.type,resolution=[s.render.resolution_x,s.render.resolution_y])
    return objects,camera

def main(before,after,output):
    a,ac=read(before);b,bc=read(after);assert ac==bc and a.keys()==b.keys();rows={4:.020,5:.055,6:.030,8:-.040,9:.020};maximum=0
    for name,old in a.items():
        new=b[name];assert old['faces']==new['faces'] and old['matrix']==new['matrix'];assert np.array_equal(old['uv'],new['uv'])
        expected=old['co'].copy()
        if 'body' in name:
            for ring,delta in rows.items():expected[ring*96:(ring+1)*96,2]+=delta
        error=float(abs(expected-new['co']).max());assert error<3e-7,(name,error);maximum=max(maximum,error)
        assert np.array_equal(old['co'][:,:2],new['co'][:,:2])
    report=dict(before=before,after=after,cameraAndFramingExact=True,atlasUvsExact=True,topologyExact=True,allRadiiExact=True,crossExact=True,onlyChangedBodyRingHeights=rows,maxExpectedPositionError=maximum)
    out=ROOT/output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_FOOT_SCOPE_PASS',json.dumps(report))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output)
