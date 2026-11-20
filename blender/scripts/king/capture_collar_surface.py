"""Capture actual king wood and coat normals; diagnostic outputs, never beauty."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls

def main(source_name,output_name,crop=None,probe_pixels=None,material_fields=False):
    source=ROOT/source_name;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    body=next(o for o in controls(s) if 'body' in o.name);mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n['Principled BSDF'];output=next(node for node in n if node.type=='OUTPUT_MATERIAL')
    geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE'
    offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.5,.5,.5)
    emission=n.new('ShaderNodeEmission');l.new(scale.outputs['Vector'],offset.inputs[0]);l.new(offset.outputs['Vector'],emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
    fields=[('position',geo.outputs['Position'],.1)]
    for name,slot in [('normal','Normal'),('coat-normal','Coat Normal')]:
        socket=bs.inputs[slot].links[0].from_socket if bs.inputs[slot].is_linked else geo.outputs['Normal'];fields.append((name,socket,.5))
    if material_fields:
        for name,node,slot in [('roughness',bs,'Roughness'),('coat-roughness',bs,'Coat Roughness'),('coat-weight',bs,'Coat Weight'),('coat-relief',n['Fine varnish relief'],'Strength')]:
            inp=node.inputs[slot]
            if inp.is_linked:socket=inp.links[0].from_socket
            else:
                scalar=n.new('ShaderNodeValue');scalar.outputs[0].default_value=inp.default_value;socket=scalar.outputs[0]
            fields.append((name,socket,.5))
        ring=n.new('ShaderNodeAttribute');ring.attribute_name='King profile ring';fields.append(('profile-ring',ring.outputs['Fac'],.01))
    out=ROOT/output_name;out.mkdir(parents=True,exist_ok=True);crop=crop or [330,390,675,555];x0,y0,x1,y1=crop
    w=s.render.resolution_x;h=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=True
    s.render.border_min_x=(x0+.01)/w;s.render.border_max_x=(x1+.01)/w;s.render.border_min_y=(h-y1+.01)/h;s.render.border_max_y=(h-y0+.01)/h
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
    s.cycles.samples=32;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.use_persistent_data=True
    arrays={}
    for name,socket,factor in fields:
        l.new(socket,scale.inputs[0]);scale.inputs['Scale'].default_value=factor;dest=out/(name+'.exr');s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
        im=bpy.data.images.load(str(dest),check_existing=False);iw,ih=im.size;assert(iw,ih)==(x1-x0,y1-y0)
        a=np.array(im.pixels[:],dtype=np.float32).reshape(ih,iw,4)[::-1].copy();bpy.data.images.remove(im);a[:,:,:3]=(a[:,:,:3]-.5)/factor
        np.save(out/(name+'.npy'),a);arrays[name]=a
    probes=[]
    for x,y in (probe_pixels or [[470,423],[555,428],[445,491],[580,477],[450,517],[566,531]]):
        assert x0+1<=x<x1-1 and y0+1<=y<y1-1
        probes.append(dict(pixel=[x,y],**{name:arrays[name][y-y0-1:y-y0+2,x-x0-1:x-x0+2,:3].mean((0,1)).tolist() for name in arrays}))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    report=dict(source=source_name,source_sha256=digest,source_unchanged=True,crop=crop,samples=32,
        normal_sources={name:socket.node.name for name,socket,_ in fields},probes=probes,
        note='Emission encodes diagnostic position and actual shader normals. No replacement Blender scene is saved.')
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--crop',type=int,nargs=4);p.add_argument('--probe',type=int,nargs=2,action='append');p.add_argument('--material-fields',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.source,a.output,a.crop,a.probe,a.material_fields)
