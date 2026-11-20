"""Photograph each actual lamp's contribution to the crest and its neighboring face."""
from pathlib import Path
import sys,json
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,proposal,border,configure_render,render,OVAL,sha
def run(key):
    s=load('parent.blend' if key.isdigit() or key=='parent' else 'knight.blend')
    if key.isdigit():proposal(s,int(key))
    configure_render(s,48);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=5;border(s)
    entries={}
    for label,name in [('oval',OVAL),('forward','Walnut | forward poll window'),('upper','Poll flag | Walnut upper strip')]:
        if name not in s.objects:continue
        s.objects[name].hide_render=True
        file=D/f'without-{label}-{key}.png';render(s,file);entries[label]=sha(file)
        s.objects[name].hide_render=False
    (D/f'controls-{key}.json').write_text(json.dumps(entries,indent=2)+'\n')
if __name__=='__main__':run(sys.argv[-1])
