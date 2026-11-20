"""Compare the actual back, opposite flank and native-size front of the carving."""
from pathlib import Path
import sys
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,sculpt,camera,configure_render,render,pose
def run(key):
    s=load('knight.blend' if key=='knight' else 'parent.blend')
    if key.isdigit():sculpt(s,int(key))
    configure_render(s,28)
    s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_percentage=48
    render(s,D/f'turn-{key}-fixed.png')
    s.render.resolution_percentage=100;s.render.resolution_x=s.render.resolution_y=384
    for name,theta in [('near',0),('rear-quarter',225),('far',180),('rear',270)]:
        camera(s,pose(s)[2]+theta)
        render(s,D/f'turn-{key}-{name}.png')
if __name__=='__main__':
    for key in sys.argv[sys.argv.index('--')+1:]:run(key)
