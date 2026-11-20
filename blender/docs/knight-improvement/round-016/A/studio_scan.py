"""Orient two actual area cards to the native shoulder; compare finite emitter dimensions."""
from pathlib import Path
import sys,numpy as np,bpy,math
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from sculpt import load,carve,lights,light_normals,configure_render,render,crop
def fit(ob,xyz,r,distance,width,energy,color,extra=.12):
 n=np.median(r,axis=0);n/=np.linalg.norm(n);p=xyz.mean(0)+distance*n
 ts=((p-xyz)@n)/(r@n);hot=xyz+r*ts[:,None];mid=hot.mean(0)
 _,_,vh=np.linalg.svd(hot-mid);ax=vh[0]-n*(vh[0]@n);ax/=np.linalg.norm(ax);ay=np.cross(n,ax);along=(hot-mid)@ax
 lo,hi=along.min(),along.max();mid+=(lo+hi)*.5*ax
 ob.location=mid;ob.rotation_euler=Matrix(np.column_stack((ax,ay,n))).to_euler();ob.data.size=max(.25,(hi-lo)*(1+extra));ob.data.size_y=width;ob.data.energy=energy;ob.data.color=color;ob.data.spread=math.radians(120)
 return [ob.data.size,ob.data.size_y,ob.data.energy]
def stage(s,k):
 grid,ref=light_normals(s);rear=s.objects['Walnut | poll rear oval'];front=s.objects['Walnut | shaped front shoulder bounce']
 if k=='warm-dome':return []
 styles={'ribbon':(156,154,1.55,.085,83,1.09,.12,15.),'shoulder':(154,151,1.50,.12,98,1.01,.18,16.),
 'incision':(158,157,1.50,.10,103,1.10,.13,13.),'edge':(155,158,1.65,.10,97,1.00,.155,18.)}
 j,k,d1,w1,e1,d2,w2,e2=styles[k];a,b=ref(grid[6:15,j]);q1=fit(rear,a,b,d1,w1,e1,(1.,.62,.32))
 a,b=ref(grid[2:8,k]);q2=fit(front,a,b,d2,w2,e2,(1.,.73,.43),.17)
 return [q1,q2]
def main():
 s=load('parent');carve(s);lights(s);configure_render(s,24);crop(s,(240,270,530,431))
 for k in ['warm-dome','ribbon','shoulder','incision','edge']:
  print(k,stage(s,k),flush=True);render(s,D/f'scan-{k}.png')
if __name__=='__main__':main()
