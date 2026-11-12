"""Read-only separation of collar pigment, diffuse form and specular finish."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls

def main(source_name,output_name):
    source=ROOT/source_name;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    body=next(o for o in controls(s) if 'body' in o.name);material=body.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
    bs=nodes['Principled BSDF'];output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');color=bs.inputs['Base Color'].links[0].from_socket
    report=dict(source=source_name,source_sha256=digest,bounds=[300,350,710,570],
        inputs={slot:dict(default=list(bs.inputs[slot].default_value) if slot in ['Normal','Coat Normal'] else bs.inputs[slot].default_value,
                    linked_from=bs.inputs[slot].links[0].from_node.name if bs.inputs[slot].is_linked else None)
                for slot in ['Roughness','Coat Weight','Coat Roughness','Specular IOR Level','Normal','Coat Normal']},
        note='All non-beauty images are diagnostic only; the source scene and reference images remain unchanged.')
    out=ROOT/output_name;out.mkdir(parents=True,exist_ok=True);w=s.render.resolution_x;h=s.render.resolution_y
    s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=300/w;s.render.border_max_x=710/w;s.render.border_min_y=1-570/h;s.render.border_max_y=1-350/h
    s.cycles.samples=128;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    def render(name):s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    render('accepted-shading')
    diffuse=nodes.new('ShaderNodeBsdfDiffuse');links.new(color,diffuse.inputs['Color'])
    if bs.inputs['Normal'].is_linked:links.new(bs.inputs['Normal'].links[0].from_socket,diffuse.inputs['Normal'])
    links.new(diffuse.outputs[0],output.inputs['Surface']);render('diffuse-only')
    pigment=nodes.new('ShaderNodeEmission');links.new(color,pigment.inputs['Color']);links.new(pigment.outputs[0],output.inputs['Surface'])
    render('pigment-agx');s.view_settings.view_transform='Standard';render('pigment-standard')
    s.view_settings.view_transform='AgX';clay=nodes.new('ShaderNodeBsdfDiffuse');clay.inputs['Color'].default_value=(.18,.18,.18,1)
    links.new(clay.outputs[0],output.inputs['Surface']);render('diffuse-clay')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    (out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_COLLAR_FINISH_DIAGNOSED')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.source,a.output)
