"""Read-only meridian comparison for the owner-directed Queen shape phase."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from refine_socket_flare import read_controls

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--after',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
    controls={};reports={}
    for name,path in [('before',a.before.resolve()),('after',a.after.resolve())]:
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
        scene=bpy.context.scene;body=editable_mesh(scene)
        c=read_controls(body.data,int(body['ring_segments']));controls[name]=c
        r=np.linalg.norm(c[:,:,:2],axis=2).mean(1);z=c[:,:,2].mean(1)
        reports[name]={
            'sha256':digest,'rings':len(c),'vertices':int(c.size//3),
            'socket_seat_height':float(z[38]),'socket_wall_height':float(z[33]-z[29]),
            'socket_wall_radius':float(r[31]),'socket_shelf_radial_span':float(r[33]-r[38]),
            'inner_flare_radius_ring_25':float(r[25]),
            'lower_collar_peak_radius':float(r[50:63].max()),
            'lower_collar_height_50_62':float(z[62]-z[50]),
            'upper_collar_peak_radius':float(r[74:83].max()),
            'upper_collar_height_74_82':float(z[82]-z[74]),
            'foot_ground_z':float(z.min()),'max_control_z':float(z.max()),
            'camera_type':scene.camera.data.type,
            'camera_matrix':[float(v) for row in scene.camera.matrix_world for v in row],
            'camera_scale':scene.camera.data.ortho_scale,
            'radii':r.tolist(),'heights':z.tolist(),
        }
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    assert reports['before']['camera_matrix']==reports['after']['camera_matrix']
    assert reports['before']['camera_scale']==reports['after']['camera_scale']
    assert np.array_equal(controls['before'][86:108],controls['after'][86:108]),'Crown/bowl should remain protected'
    reports['preservation']={'camera_exact':True,'crown_bowl_controls_86_to_107_exact':True,'sources_read_only':True}
    np.savez_compressed(a.output/'phase-controls.npz',**controls)
    (a.output/'phase-measurements.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps({key:{k:v for k,v in val.items() if k not in ['radii','heights','camera_matrix']} for key,val in reports.items()},indent=2))

if __name__=='__main__':main()
