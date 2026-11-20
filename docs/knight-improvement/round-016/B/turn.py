"""Look across the real crest from either side as one broad area light moves."""
from pathlib import Path
import sys,math,json
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,proposal,pose,posed,configure_render,render,sha
from mission_scene import visible_meshes
def run(key,quick=False):
    s=load('knight.blend' if key=='knight' else 'parent.blend')
    if key.isdigit():proposal(s,int(key))
    p=pose(s);a=math.radians(p[2]);along=Vector((math.cos(a),math.sin(a),0));across=Vector((-along.y,along.x,0))
    up=Vector((0,0,1));center=Vector(posed(np.array([[-.36,0.,4.87]]),*p)[0])
    configure_render(s,32 if not quick else 24);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_x=500;s.render.resolution_y=270;s.render.resolution_percentage=100;s.render.use_border=s.render.use_crop_to_border=False
    s.camera.data.ortho_scale=1.96;s.camera.data.shift_x=s.camera.data.shift_y=0
    for o in s.objects:
        if o.type=='LIGHT':o.hide_render=True
    s.world=bpy.data.worlds.new('Neutral crown studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.23
    def lamp(n,power,width):
        l=bpy.data.lights.new(n,'AREA');l.shape='DISK';l.energy=power;l.size=width
        o=bpy.data.objects.new(n,l);s.collection.objects.link(o);return o
    primary=lamp('Moving walnut bank',215,2.1);fill=lamp('Opposite crown fill',52,3.7)
    clay=bpy.data.materials.new('Neutral crest clay');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.4,.42,.43,1);bs.inputs['Roughness'].default_value=.52
    record={}
    for mat in ['walnut','clay']:
        if mat=='clay':
            for o in visible_meshes(s):
                for slot in o.material_slots:slot.material=clay
        for label,sign in [('near',-1),('far',1)]:
            aim=center;cam=s.camera;cam.location=aim+7*(sign*across+.04*along+.22*up)
            cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
            fill.location=center-sign*across*2.2+1.8*up
            fill.rotation_euler=(aim-fill.location).to_track_quat('-Z','Y').to_euler()
            for idx,(x,z) in enumerate([(-2.6,2.1),(.05,3.5),(2.6,2.3)]):
                if quick and idx!=1:continue
                primary.location=center+x*along+sign*2.8*across+z*up
                primary.rotation_euler=(aim-primary.location).to_track_quat('-Z','Y').to_euler()
                file=D/f'turn-{key}-{label}-{mat}-{idx}.png';render(s,file);record[file.name]=sha(file)
    (D/f'turn-{key}.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    for key in list(filter(lambda a:a!='--quick',args)):run(key,'--quick' in args)
