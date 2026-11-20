"""Measure the individual contributions of the unchanged studio and two physical poll cards."""
from pathlib import Path
import sys,json
import bpy
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from sculpt import load,carve,lights,crop,configure_render,render
s=load('parent');carve(s);configure_render(s,24);crop(s,(240,270,530,431));rear=s.objects['Walnut | poll rear oval'];parent=(rear.matrix_world.copy(),rear.data.size,rear.data.size_y,rear.data.energy,list(rear.data.color))
render(s,D/'meter-original.png');desc=lights(s);print('rig',desc,flush=True);front=s.objects['Walnut | shaped front shoulder bounce']
front.data.energy=0;render(s,D/'meter-rear.png')
rear.data.energy=0;front.data.energy=4.;front.data.size=.29;front.data.size_y=.17;front.data.spread=2.0;render(s,D/'meter-front.png')
rear.matrix_world=parent[0];rear.data.size=parent[1];rear.data.size_y=.085;rear.data.energy=89;rear.data.color=(1.,.66,.36);render(s,D/'meter-mixed.png')
