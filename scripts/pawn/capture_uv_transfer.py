"""Capture actual old UVs and new visibility for a bounded surface-map transfer.

Emission passes are coordinate diagnostics only. Neither source scene is saved.
"""
import argparse,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import ROOT,BUILD,save_json,sha
from capture_pigment import meridian_samples,UV_NAME

def run(cfg):
    out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    for label in ('old','new'):
        scene,body=open_source({**cfg[label],'samples':16})
        scene.cycles.use_denoising=False;scene.cycles.use_adaptive_sampling=False
        scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
        mat=body.data.materials[0];nodes,links=mat.node_tree.nodes,mat.node_tree.links
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        emitter=nodes.new('ShaderNodeEmission');emitter.inputs['Strength'].default_value=1
        links.new(emitter.outputs[0],output.inputs['Surface'])
        if label=='old':
            uv=nodes.new('ShaderNodeUVMap');uv.uv_map=UV_NAME
            split=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs[0],split.inputs[0])
            geom=nodes.new('ShaderNodeNewGeometry');xyz=nodes.new('ShaderNodeSeparateXYZ')
            links.new(geom.outputs['Position'],xyz.inputs[0])
            comb=nodes.new('ShaderNodeCombineXYZ')
            links.new(split.outputs['X'],comb.inputs['X']);links.new(split.outputs['Y'],comb.inputs['Y'])
            links.new(xyz.outputs['Z'],comb.inputs['Z']);links.new(comb.outputs[0],emitter.inputs['Color'])
        else:
            np.save(out/'new-meridian.npy',meridian_samples(body))
            cam=nodes.new('ShaderNodeCameraData');links.new(cam.outputs['View Z Depth'],emitter.inputs['Color'])
        scene.render.filepath=str(out/(label+'.exr'));bpy.ops.render.render(write_still=True)
        image=bpy.data.images.load(scene.render.filepath,check_existing=False)
        w,h=image.size;pixels=np.empty(w*h*4,np.float32);image.pixels.foreach_get(pixels)
        np.save(out/(label+'.npy'),pixels.reshape(h,w,4)[::-1].copy());bpy.data.images.remove(image)
    save_json(out/'measurement.json',{'config':cfg,'old_uv_z_sha256':sha(out/'old.npy'),
        'new_depth_sha256':sha(out/'new.npy'),'new_meridian_sha256':sha(out/'new-meridian.npy'),
        'note':'Old UV and world Z; new camera depth and evaluated meridian. Sources are opened by hash, never saved.'})
    print('UV transfer measurements complete.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
