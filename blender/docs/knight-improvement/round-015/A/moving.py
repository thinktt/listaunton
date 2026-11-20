"""Move a physical studio key over the head while the camera and carving stay fixed."""
from pathlib import Path
import sys,math,json,hashlib
import bpy
from mathutils import Vector
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from diagnostic_views import open_model,configure_render,render,visible_meshes
from mission_scene import sha
def run():
    outputs={}
    for n in ['parent','knight']:
        s=open_model(n+'.blend');yaw=math.radians(json.loads(s['knight_mission_pose'])['twist_degrees'])
        axis=Vector((math.cos(yaw),math.sin(yaw),0));side=Vector((axis.y,-axis.x,0));up=Vector((0,0,1))
        target=s.objects['Knight | near eye'].matrix_world.translation.copy()
        for ob in s.objects:
            if ob.type=='LIGHT':ob.hide_render=True
        def area(name,power,size):
            l=bpy.data.lights.new(name,'AREA');l.shape='DISK';l.energy=power;l.size=size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);return o
        key=area('Moving broad light',285,2.6);fill=area('Fixed soft fill',62,4.2)
        fill.location=target+3*side+.4*axis+2*up;fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
        s.world=bpy.data.worlds.new('Soft studio ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.24
        configure_render(s,24);s.render.resolution_x=448;s.render.resolution_y=318
        cam=s.camera;cam.data.ortho_scale=1.78;cam.data.shift_x=cam.data.shift_y=0
        cam.location=target+7*(side+.17*axis+.18*up);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        for mat in ['wood','clay']:
            if mat=='clay':
                plain=bpy.data.materials.new('Moving-light clay');plain.use_nodes=True;bs=plain.node_tree.nodes['Principled BSDF']
                bs.inputs['Base Color'].default_value=(.4,.42,.43,1);bs.inputs['Roughness'].default_value=.62
                for o in visible_meshes(s):
                    for slot in o.material_slots:slot.material=plain
            for i,angle in enumerate([-56,-30,0,30,56]):
                a=math.radians(angle);key.location=target+3.45*side+3.85*math.sin(a)*axis+3.85*math.cos(a)*up
                key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
                path=D/'moving'/f'{n}-{mat}-{i}.png';path.parent.mkdir(exist_ok=True)
                render(s,path);outputs[path.name]=sha(path)
    (D/'moving.json').write_text(json.dumps({'model':sha(D/'knight.blend'),'parent':sha(D/'parent.blend'),'views':outputs,'light_arc_degrees':[-56,-30,0,30,56]},indent=2)+'\n')
if __name__=='__main__':run()
