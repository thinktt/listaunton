"""Inspect which physical part of the lower softbox and the cheek face one another."""
import bpy,numpy as np,sys
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,DESIGNS,sculpt
from lamps import rays
def inspect(i):
    s=load('parent.blend');sculpt(s,DESIGNS[i])
    for kind in (False,True):
        ob=s.objects['Eye reflection '+('upper' if kind else 'lower')]
        m=np.asarray(ob.matrix_world);loc=m[:3,3];rot=m[:3,:3];n=rot[:,2]
        print(ob.name,ob.data.energy,ob.data.size,ob.data.size_y, 'linked',[o.name for o in ob.light_linking.receiver_collection.objects] if ob.light_linking.receiver_collection else None)
        for x,y,v in rays(s,kind):
            k=((loc-y)@n)/(v@n)
            delta=(y+k*v-loc)@rot
            print(x,np.round(delta[:2]/[ob.data.size*.5,ob.data.size_y*.5],2),round(float(k),2))
if __name__=='__main__':inspect(int(sys.argv[-1]))
