"""Read-only socket pigment and shading separation; never a final render."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls
from focused_reflections import target


def main(source_name,output_name):
    source=ROOT/source_name;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    out=ROOT/output_name;out.mkdir(parents=True,exist_ok=True)
    material=controls(s)[0].data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
    bs=nodes['Principled BSDF'];output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    color=bs.inputs['Base Color'].links[0].from_socket
    w=s.render.resolution_x;h=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=330/w;s.render.border_max_x=680/w;s.render.border_min_y=1-845/h;s.render.border_max_y=1-680/h
    s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    def render(name):
        s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    render('accepted-shading')
    diffuse=nodes.new('ShaderNodeBsdfDiffuse');links.new(color,diffuse.inputs['Color'])
    if bs.inputs['Normal'].is_linked:links.new(bs.inputs['Normal'].links[0].from_socket,diffuse.inputs['Normal'])
    links.new(diffuse.outputs[0],output.inputs['Surface']);render('diffuse-only')
    pigment=nodes.new('ShaderNodeEmission');links.new(color,pigment.inputs['Color']);links.new(pigment.outputs[0],output.inputs['Surface'])
    render('pigment-only-agx')
    s.view_settings.view_transform='Standard';render('pigment-only-standard')
    probes=[]
    for x,y in [(440,742),(465,748),(500,754),(550,748),(580,740),(465,769),(555,772)]:
        ob,p,d,n=target(s,x,y)
        probes.append(dict(pixel=[x,y],point=list(p),normal=list(n),reflection=list(d),receiver=ob.get('king_render_region')))
    report=dict(source=source_name,source_sha256=digest,color_source_node=color.node.name,color_source_socket=color.name,
                bounds=[330,680,680,845],probes=probes,note='Diffuse and emission views are diagnostic only; no replacement model is saved.')
    (out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    print('KING_SOCKET_FINISH_DIAGNOSTIC_DONE')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.source,a.output)
