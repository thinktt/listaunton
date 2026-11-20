"""Aim strip reflectors from measured bevel normals; isolated checkpoint-025 trials."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'history/rook-mission-025/models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='082b79a1712cd07eaab76af0f945688ff04281ba9678e568ac1077698ad7b8a2'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
rim=next(o for o in s.objects if o.get('rook_render_receiver')=='rim');m=rim.data
view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
points=[]
for label,xy,outer in [('rear-inner',(390,312),False),('front-outer',(420,543),True)]:
    candidates=[];proj=s.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1254,y=1254)@s.camera.matrix_world.inverted()
    for loop in m.loops:
        p=m.vertices[loop.vertex_index].co;n=m.corner_normals[loop.index].vector
        radius=(p.x*p.x+p.y*p.y)**.5
        if p.z<2.728 or not .75<n.z<.95:continue
        if outer and radius<.62:continue
        if not outer and radius>.57:continue
        q=proj@p.to_4d();pixel=((q.x/q.w+1)*627,(1-q.y/q.w)*627)
        candidates.append(((pixel[0]-xy[0])**2+(pixel[1]-xy[1])**2,p.copy(),n.copy(),pixel))
    dist,p,n,pixel=min(candidates,key=lambda row:row[0]);direction=(2*n.dot(view)*n-view).normalized();position=p+direction*4
    points.append({'label':label,'target_pixel':xy,'actual_pixel':pixel,'point':list(p),'normal':list(n),'position':list(position),'pixel_distance':dist**.5})
receiver=bpy.data.collections.new('Normal strip rim only');receiver.objects.link(rim)
for number,row in zip([33,34],points):
    d=bpy.data.lights.new('Measured rim '+row['label'],'AREA');d.shape='RECTANGLE';d.size=6;d.size_y=.12;d.energy=300
    ob=bpy.data.objects.new(d.name,d);s.collection.objects.link(ob);ob.location=row['position'];ob.rotation_euler=(Vector(row['point'])-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_diffuse=False;ob.light_linking.receiver_collection=receiver
    out=ROOT/f'build/rook-mission/{number:03d}-measured-rim';out.mkdir(exist_ok=True,parents=True)
    s.cycles.samples=64;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'reflectors':points[:number-32],'watts_each':300,'size':[6,.12]},indent=2)+'\n')
    print('MEASURED_RIM_DONE',number,flush=True)
