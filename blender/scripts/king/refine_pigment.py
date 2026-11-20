"""Transfer bounded fine reference grain in shader space, excluding broad lighting."""
from pathlib import Path
import argparse,json,sys,hashlib
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes

def main(cfg):
    source=ROOT/cfg['source'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;mat=meshes(scene)[0].data.materials[0]
    n=mat.node_tree.nodes;l=mat.node_tree.links
    tex=n['Derived king pigment'];uv=tex.inputs['Vector'].links[0].from_socket
    grade=n['Pigment grade'];grade.inputs['Value'].default_value=cfg.get('value',.76);grade.inputs['Saturation'].default_value=cfg.get('saturation',.93)
    def blur(image,pixels,steps):
        sums=None;count=0
        for y in range(-steps,steps+1):
            for x in range(-steps,steps+1):
                offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';l.new(uv,offset.inputs[0]);offset.inputs[1].default_value=(x*pixels/image.size[0],y*pixels/image.size[1],0)
                sample=n.new('ShaderNodeTexImage');sample.image=image;sample.extension='EXTEND';l.new(offset.outputs['Vector'],sample.inputs['Vector']);count+=1
                if sums is None:sums=sample.outputs['Color']
                else:
                    add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(sums,add.inputs[0]);l.new(sample.outputs['Color'],add.inputs[1]);sums=add.outputs['Vector']
        scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/count;l.new(sums,scale.inputs[0]);return scale.outputs['Vector']
    broad=blur(tex.image,cfg.get('broad_step',7),2);l.new(broad,grade.inputs['Color'])
    reference=bpy.data.images.load(str(ROOT/'assets/king/reference.png'),check_existing=False);reference.pack()
    fine=n.new('ShaderNodeTexImage');fine.image=reference;fine.extension='EXTEND';l.new(uv,fine.inputs['Vector'])
    blurred=blur(reference,cfg.get('fine_step',3),1)
    def gray(socket):
        node=n.new('ShaderNodeRGBToBW');l.new(socket,node.inputs[0]);return node.outputs[0]
    safe=n.new('ShaderNodeMath');safe.operation='MAXIMUM';safe.inputs[1].default_value=.003;l.new(gray(blurred),safe.inputs[0])
    ratio=n.new('ShaderNodeMath');ratio.operation='DIVIDE';l.new(gray(fine.outputs['Color']),ratio.inputs[0]);l.new(safe.outputs[0],ratio.inputs[1])
    lo=n.new('ShaderNodeMath');lo.operation='MAXIMUM';lo.inputs[1].default_value=.55;l.new(ratio.outputs[0],lo.inputs[0])
    hi=n.new('ShaderNodeMath');hi.operation='MINIMUM';hi.inputs[1].default_value=1.55;l.new(lo.outputs[0],hi.inputs[0])
    gain=n.new('ShaderNodeMath');gain.operation='POWER';gain.inputs[1].default_value=cfg.get('grain_gain',.8);l.new(hi.outputs[0],gain.inputs[0])
    pigment=n.new('ShaderNodeVectorMath');pigment.operation='SCALE';l.new(grade.outputs[0],pigment.inputs[0]);l.new(gain.outputs[0],pigment.inputs['Scale'])
    l.new(pigment.outputs['Vector'],n['Continuous pigment'].inputs[2])
    bump=n['Pigment microrelief'];l.new(gain.outputs[0],bump.inputs['Height']);bump.inputs['Strength'].default_value=cfg.get('relief_strength',.1);bump.inputs['Distance'].default_value=cfg.get('relief_distance',.002)
    if cfg.get('coat_microrelief'):
        l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Coat Normal'])
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=str((out/'prepared.blend').relative_to(ROOT)),original_source=cfg['source'],original_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),fine_reference_sha256=hashlib.sha256((ROOT/'assets/king/reference.png').read_bytes()).hexdigest(),grain_ratio_bounds=[.55,1.55])
    run(rendercfg)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
