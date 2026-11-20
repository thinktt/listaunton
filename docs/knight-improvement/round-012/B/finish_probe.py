"""Separate inherited wood pigment, native form and studio finish on the carving."""
from pathlib import Path
import sys
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import configure_render,load,sculpt,crop,render,MANE

def setup(s):
    configure_render(s,36);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=3
    crop(s,(175,374,436,716))

def run(key,mode):
    s=load('knight.blend' if key=='knight' else 'parent.blend')
    if key.isdigit():sculpt(s,int(key))
    setup(s)
    if mode in ('albedo','uniform'):
        mat=s.objects['Knight | '+MANE].active_material
        nt=mat.node_tree
        alb=nt.nodes.get('Knight delivered albedo')
        if mode=='albedo':
            emit=nt.nodes.new('ShaderNodeEmission')
            nt.links.new(alb.outputs['Color'],emit.inputs['Color'])
            nt.links.new(emit.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
        else:
            for node in nt.nodes:
                if node.type=='BSDF_PRINCIPLED':
                    inp=node.inputs['Base Color']
                    for link in list(inp.links):nt.links.remove(link)
                    inp.default_value=(.10,.042,.011,1.)
    render(s,D/f'finish-{key}-{mode}.png')
if __name__=='__main__':
    for key in sys.argv[sys.argv.index('--')+1:]:
        for mode in ['albedo','uniform']:run(key,mode)
