"""Estimate diffuse pigment from measured real-BSDF light response.

This is inverse material estimation, not a composited beauty replacement.
Bright glints, underexposed shadows, absent geometry and specular-dominated
pixels retain the previous pigment. The unknown rear finish is unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np,PyOpenColorIO as ocio
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes

def pixels(image):
    w,h=image.size;out=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(out);return out.reshape(h,w,4)[::-1].copy()

def main(cfg):
    response=ROOT/cfg['response'];info=json.loads((response/'response.json').read_text());source=ROOT/info['source']
    digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==info['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    assert s.view_settings.look=='None' and s.view_settings.exposure==0 and s.view_settings.gamma==1
    black=np.load(response/'black.npy');white=np.load(response/'white.npy')
    original=bpy.data.images.load(str(ROOT/'assets/king/reference.png'),check_existing=False)
    # Byte-backed PNG pixels are stored encoded, unlike float EXR pixels.
    # Verified against Pillow: (500,700) is RGBA (79,31,3,251) in this source.
    assert not original.is_float and original.colorspace_settings.name=='sRGB'
    raw=pixels(original);display=(raw[:,:,:3]*raw[:,:,3:4]).astype(np.float32)
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');transform.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    target=display.copy();config.getProcessor(transform).getDefaultCPUProcessor().applyRGB(target)
    diffuse=np.maximum(white[:,:,:3]-black[:,:,:3],0)
    inferred=(target-black[:,:,:3])/np.maximum(diffuse,.008)
    pigment=np.clip(inferred,.001,.8).astype(np.float32)
    luminance=np.array([.2126,.7152,.0722],dtype=np.float32)
    target_lum=target@luminance;spec_lum=black[:,:,:3]@luminance;response_lum=diffuse@luminance
    reliability=np.clip((response_lum-.015)/.08,0,1)
    reliability*=np.clip(((display@luminance)-.025)/.07,0,1)
    reliability*=np.clip((.36-display.min(2))/.20,0,1)
    reliability*=np.clip((.8-spec_lum/np.maximum(target_lum,.008))/.5,0,1)
    # The supplied cutout has small alpha variations within the solid piece.
    # A .99 threshold incorrectly turns those variations into a mottled mask.
    reliability*=np.clip((raw[:,:,3]-.8)/.1,0,1)*(white[:,:,3]>.99)*(display.max(2)>.05)
    reliability*=cfg.get('strength',.9)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
    def image(name,rgb):
        rgba=np.dstack([rgb,np.ones(rgb.shape[:2],dtype=np.float32)]).astype(np.float32);h,w=rgba.shape[:2]
        im=bpy.data.images.new(name,width=w,height=h,alpha=False,float_buffer=True);im.colorspace_settings.name='Linear Rec.709'
        im.pixels.foreach_set(rgba[::-1].copy().reshape(-1));im.file_format='OPEN_EXR';im.filepath_raw=str(out/(name+'.exr'));im.save();im.pack();return im
    color=image('king-recovered-pigment',pigment);confidence=image('king-pigment-confidence',np.repeat(reliability[:,:,None],3,axis=2))
    objects=meshes(s)
    scoped=info.get('partial_object_response',False)
    if scoped:
        assert set(info['object_names']).issubset({ob.name for ob in objects})
        for ob in objects:
            attr=ob.data.attributes.get('Pigment response region') or ob.data.attributes.new('Pigment response region','FLOAT','POINT')
            value=1.0 if ob.name in info['object_names'] else 0.0
            attr.data.foreach_set('value',np.full(len(ob.data.vertices),value,dtype=np.float32))
    for ob in objects:
        uv=ob.data.uv_layers.get('Response pigment') or ob.data.uv_layers.new(name='Response pigment');coords=[]
        for v in ob.data.vertices:
            p=world_to_camera_view(s,s.camera,ob.matrix_world@v.co);coords.append((p.x,p.y))
        for loop in ob.data.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
    mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];previous=bs.inputs['Base Color'].links[0].from_socket
    uv=n.new('ShaderNodeUVMap');uv.uv_map='Response pigment'
    a=n.new('ShaderNodeTexImage');a.name='Estimated diffuse pigment';a.image=color;a.extension='EXTEND';l.new(uv.outputs[0],a.inputs['Vector'])
    c=n.new('ShaderNodeTexImage');c.name='Pigment estimation confidence';c.image=confidence;c.extension='EXTEND';l.new(uv.outputs[0],c.inputs['Vector'])
    attribute=n.new('ShaderNodeAttribute');attribute.attribute_name='Pigment coverage'
    weight=n.new('ShaderNodeMath');weight.operation='MULTIPLY';l.new(c.outputs['Color'],weight.inputs[0]);l.new(attribute.outputs['Fac'],weight.inputs[1])
    factor=weight.outputs[0]
    if scoped:
        region=n.new('ShaderNodeAttribute');region.attribute_name='Pigment response region'
        gate=n.new('ShaderNodeMath');gate.operation='MULTIPLY';l.new(factor,gate.inputs[0]);l.new(region.outputs['Fac'],gate.inputs[1]);factor=gate.outputs[0]
    mix=n.new('ShaderNodeMixRGB');mix.name='Measured pigment with bounded confidence';l.new(factor,mix.inputs[0]);l.new(previous,mix.inputs[1]);l.new(a.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    s['king_recovered_pigment_method']='Inverse local real-BSDF black/white response, confidence-masked; live specular/coat and all lights retained.'
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=info['source'],original_source_sha256=digest,reference_sha256=hashlib.sha256((ROOT/'assets/king/reference.png').read_bytes()).hexdigest(),reference_pixel_500_700=list(map(float,raw[700,500])),pigment_bounds=[.001,.8],confidence_mean_foreground=float(reliability[white[:,:,3]>.99].mean()),fraction_foreground_over_half_confidence=float((reliability[white[:,:,3]>.99]>.5).mean()),limitation='Low-confidence regions use prior pigment. Inversion is approximate because of multibounce light and single-view ambiguity; it is not a unique recovered albedo.')
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'));run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
