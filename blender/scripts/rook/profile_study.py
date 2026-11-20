"""Scoped turning edits under the high-strip diagnostic, never public outputs."""
from pathlib import Path
import sys,json,hashlib
import bpy,numpy as np,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/010-high-strip/rook.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='da8a86da03de5ffd0cf1d99fa1170ef80bd033fe851c01c6770b7a47e9c65298'
shoulder={19:195,20:193,21:194,22:196,23:198};foot={7:245,8:244,9:244,10:246,11:248}
for name,edits in [('012-shallow-shoulder',shoulder),('013-shallow-foot',foot),('014-shallow-both',shoulder|foot)]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
    original=np.array([v.co[:] for v in body.data.vertices],np.float32).reshape(-1,128,3);co=original.copy()
    for index,radius_px in edits.items():
        radius=np.linalg.norm(co[index,:,:2],axis=1);co[index,:,:2]*=(radius_px/280/radius)[:,None]
    assert np.array_equal(co[:,:,2],original[:,:,2])
    untouched=[i for i in range(len(co)) if i not in edits];assert np.array_equal(co[untouched],original[untouched])
    body.data.vertices.foreach_set('co',co.reshape(-1));body.data.update();bpy.context.view_layer.update()
    evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free();evaluated.to_mesh_clear()
    out=ROOT/'build/rook-mission'/name;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'radial_controls_px':edits,'all_heights_exact':True,'other_control_positions_exact':True,'closed_positive_volume':volume,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()},indent=2)+'\n')
    cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
    print('PROFILE_STUDY_DONE',name,flush=True)
