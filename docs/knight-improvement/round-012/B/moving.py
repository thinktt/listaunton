"""Move one real softbox across both real flanks in common neutral clay."""
from pathlib import Path
import json,math,sys
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,configure_render,crop,render,camera,pose,sha
from mission_scene import visible_meshes

def light(s,name,energy,diameter):
    ld=bpy.data.lights.new(name,'AREA');ld.shape='DISK';ld.size=diameter;ld.energy=energy
    o=bpy.data.objects.new(name,ld);s.collection.objects.link(o);return o
def aim(o,pos,where):
    o.location=pos;o.rotation_euler=(where-pos).to_track_quat('-Z','Y').to_euler()
def run():
    files={}
    for label in ['parent','knight']:
        s=load(label+'.blend');configure_render(s,32)
        s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
        s.render.resolution_x=s.render.resolution_y=520
        for o in s.objects:
            if o.type=='LIGHT':o.hide_render=True
        for o in visible_meshes(s):
            for slot in o.material_slots:slot.material=bpy.data.materials['Neutral satin clay']
        key=light(s,'Moving bank',410,3.)
        fill=light(s,'Stationary fill',65,4.)
        angle=pose(s)[2];rad=math.radians(angle)
        along=Vector((math.cos(rad),math.sin(rad),0));side=Vector((along.y,-along.x,0));up=Vector((0,0,1))
        target=Vector((-.97,-.15,3.40))
        for flank,sg,cut in [('near',1,(72,42,317,352)),('far',-1,(218,42,459,352))]:
            camera(s,angle+(180 if sg<0 else 0))
            crop(s,cut);aim(fill,target+sg*4.1*side+2.4*up,target)
            for j,x in enumerate([-3.8,0,3.8]):
                aim(key,target+sg*3.15*side+2.64*up+x*along,target)
                pic=D/f'moving-{label}-{flank}-{j}.png';render(s,pic);files[pic.name]=sha(pic)
    (D/'moving.json').write_text(json.dumps(files,indent=2)+'\n')
if __name__=='__main__':run()
