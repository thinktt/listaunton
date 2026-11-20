"""Rotate a real broad light across the parent and candidate without changing the geometry."""
from pathlib import Path
import json,math,sys
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,portrait_setup,configure_render,render,pose
from mission_scene import sha
def main():
    files={}
    cases=[(label,file,sg) for label,file in [('parent','parent.blend'),('B','knight.blend')] for sg in (-1,1)]
    for label,file,sg in cases:
        s=load(file);configure_render(s,30);portrait_setup(s,sg)
        s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
        t=math.radians(pose(s)[2]);along=Vector((math.cos(t),math.sin(t),0))
        side=sg*Vector((-along.y,along.x,0));up=Vector((0,0,1))
        name_side='near' if sg<0 else 'far'
        center=s.objects['Knight | '+name_side+' eye'].matrix_world.translation.copy()
        for o in s.objects:
            if o.type=='LIGHT':o.hide_render=True
        def lamp(n,power,size):
            l=bpy.data.lights.new(n,'AREA');l.shape='DISK';l.energy=power;l.size=size
            o=bpy.data.objects.new(n,l);s.collection.objects.link(o);return o
        key=lamp('Orbiting carving light',245,2.45);fill=lamp('Fixed ambient card',65,4.)
        fill.location=center+side*3.+along*.4+up*2.
        fill.rotation_euler=(center-fill.location).to_track_quat('-Z','Y').to_euler()
        mat=bpy.data.materials.new('Moving-light clay');mat.use_nodes=True
        bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.40,.42,.43,1);bs.inputs['Roughness'].default_value=.62
        for mode in ['walnut','clay']:
            if mode=='clay':
                for o in s.objects:
                    if o.type=='MESH' and not o.hide_render:
                        for slot in o.material_slots:slot.material=mat
            for i,(length,z) in enumerate([(-3.,2.7),(-.3,3.9),(2.7,2.5)]):
                key.location=center+side*3.55+along*length+up*z
                key.rotation_euler=(center-key.location).to_track_quat('-Z','Y').to_euler()
                name=f'moving-{label}-{name_side}-{mode}-{i}.png';render(s,D/name);files[name]=sha(D/name)
    (D/'moving-light.json').write_text(json.dumps(files,indent=2)+'\n')
if __name__=='__main__':main()
