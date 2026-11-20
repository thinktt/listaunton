"""Fresh geometry-only measurement for static material completion."""
import argparse,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,save_json,sha
from polish_trial import open_source
from capture_pigment import meridian_samples
from fit_lighting import response
from validate_finish_scope import fingerprint

def run(cfg):
    scene,body=open_source(cfg);out=ROOT/cfg['output'];out.mkdir(parents=True,exist_ok=True)
    meridian=meridian_samples(body);np.save(out/'meridian.npy',meridian)
    profile=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)[:,0]
    save_json(out/'controls.json',profile.tolist())
    scope=fingerprint(scene,body)
    material=body.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    emit=nodes.new('ShaderNodeEmission');cam=nodes.new('ShaderNodeCameraData')
    links.new(cam.outputs['View Z Depth'],emit.inputs['Color']);links.new(emit.outputs[0],output.inputs['Surface'])
    scene.cycles.samples=12;scene.cycles.use_denoising=False
    scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
    depth=response(scene,out);np.save(out/'depth.npy',depth)
    report={'source_sha256':cfg['source_sha256'],'mesh_normals_uv_sha256':scope['evaluated_mesh_normals_uv_sha256'],
        'reference_camera_elevation':54,'meridian_shape':list(meridian.shape),
        'depth_sha256':sha(out/'depth.npy'),'meridian_sha256':sha(out/'meridian.npy')}
    if cfg.get('previous'):
        old=ROOT/cfg['previous'];old_meridian=np.load(old/'meridian.npy');old_depth=np.load(old/'depth.npy')
        report.update(previous_meridian_shape=list(old_meridian.shape),
            meridian_max_difference=float(np.max(np.abs(meridian-old_meridian))) if meridian.shape==old_meridian.shape else None,
            depth_max_difference=float(np.max(np.abs(depth-old_depth))))
    save_json(out/'measurement.json',report);print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text()))
