"""Bake the king's pigment into an atlas, retaining the actual BSDF and lighting."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes,gpu

def main(cfg):
    source=ROOT/cfg['source']
    if cfg.get('source_sha256'):assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;objects=meshes(s);body=next(ob for ob in objects if 'body' in ob.name);cross=next(ob for ob in objects if 'cross' in ob.name)
    co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3);r=np.linalg.norm(co[:,:,:2],axis=2).mean(1);z=co[:,:,2].mean(1)
    arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];arc/=arc[-1]
    uv=body.data.uv_layers.get('Pigment atlas') or body.data.uv_layers.new(name='Pigment atlas')
    for face in body.data.polygons:
        us=[((body.data.loops[li].vertex_index%96)/96-.25)%1 for li in face.loop_indices];seam=len(us)==4 and max(us)-min(us)>.5
        for li,u in zip(face.loop_indices,us):
            ri=body.data.loops[li].vertex_index//96
            uv.data[li].uv=(.01+.77*(u+(1 if seam and u<.5 else 0)),.01+.98*arc[ri])
    body.data.uv_layers.active=uv;uv.active_render=True
    for ob in bpy.context.selected_objects:ob.select_set(False)
    cross.select_set(True);bpy.context.view_layer.objects.active=cross
    cuv=cross.data.uv_layers.get('Pigment atlas') or cross.data.uv_layers.new(name='Pigment atlas');cross.data.uv_layers.active=cuv;cuv.active_render=True
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.03);bpy.ops.object.mode_set(mode='OBJECT')
    # Edit-mode UV operators invalidate the earlier layer wrapper. Reacquire it
    # before setting the packed island coordinates, and verify disjoint ranges.
    cuv=cross.data.uv_layers['Pigment atlas']
    coords=np.array([row.uv[:] for row in cuv.data],dtype=np.float32)
    coords[:,0]=.8+.19*coords[:,0];coords[:,1]=.01+.98*coords[:,1]
    cuv.data.foreach_set('uv',coords.reshape(-1));cross.data.update()
    assert max(row.uv.x for row in body.data.uv_layers['Pigment atlas'].data)<.781
    assert min(row.uv.x for row in cuv.data)>.799
    mat=body.data.materials[0];assert cross.data.materials[0]==mat
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');output=next(x for x in n if x.type=='OUTPUT_MATERIAL')
    emission=n.new('ShaderNodeEmission');l.new(bs.inputs['Base Color'].links[0].from_socket,emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
    atlas=bpy.data.images.new('King pigment atlas '+Path(cfg['texture']).stem,width=2048,height=2048,alpha=False);atlas.colorspace_settings.name='sRGB';atlas_name=atlas.name
    target=n.new('ShaderNodeTexImage');target.image=atlas;target.name='Baked pigment only'
    for node in n:node.select=False
    target.select=True;n.active=target
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=body;gpu(s);s.cycles.samples=1;s.render.bake.margin=6
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    atlaspath=ROOT/cfg['texture'];atlaspath.parent.mkdir(parents=True,exist_ok=True);atlas.filepath_raw=str(atlaspath);atlas.file_format='PNG';atlas.save();atlas.pack()
    l.new(bs.outputs['BSDF'],output.inputs['Surface']);n.remove(emission)
    uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='Pigment atlas';l.new(uvnode.outputs[0],target.inputs['Vector']);l.new(target.outputs['Color'],bs.inputs['Base Color'])
    s['king_pigment_image']=atlas_name;s['king_pigment_atlas']=cfg['texture'];s['king_pigment_uv']='Pigment atlas';s['king_pigment_atlas_bakes_lighting']=False
    before=np.array(atlas.pixels[:],dtype=np.float32)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(out/'prepared.blend'),load_ui=False)
    packed=bpy.data.images[atlas_name];after=np.array(packed.pixels[:],dtype=np.float32)
    error=float(np.max(np.abs(before-after)));assert error<1/255+.0001,error
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'};rendercfg.update(source=str((out/'prepared.blend').relative_to(ROOT)),original_source=cfg['source'],original_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),atlas_sha256=hashlib.sha256(atlaspath.read_bytes()).hexdigest(),packed_pixel_roundtrip_max_error=error,atlas_bakes_lighting=False)
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
