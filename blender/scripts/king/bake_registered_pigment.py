"""Bake a base pigment correction without rewrapping the accepted atlas UVs."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu,run
from render_regions import controls,regenerate

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;objects=controls(s)
    body=next(o for o in objects if 'body' in o.name);cross=next(o for o in objects if 'cross' in o.name)
    old=bpy.data.images[s['king_pigment_image']];assert tuple(old.size)==(2048,2048) and not old.is_float
    previous=np.array(old.pixels[:],dtype=np.float32).reshape(2048,2048,4)
    uv=body.data.uv_layers['Pigment atlas'];threshold=max(row.uv.y for row,loop in zip(uv.data,body.data.loops) if loop.vertex_index//96==24)
    preserve_from_row=int(np.ceil(threshold*2048))+8
    for ob in objects:ob.data.uv_layers.active=ob.data.uv_layers['Pigment atlas'];ob.data.uv_layers.active.active_render=True
    mat=body.data.materials[0];assert mat==cross.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];outnode=next(x for x in n if x.type=='OUTPUT_MATERIAL')
    emission=n.new('ShaderNodeEmission');l.new(bs.inputs['Base Color'].links[0].from_socket,emission.inputs['Color']);l.new(emission.outputs[0],outnode.inputs['Surface'])
    atlas=bpy.data.images.new('King pigment atlas '+Path(cfg['texture']).stem,width=2048,height=2048,alpha=False);atlas.colorspace_settings.name='sRGB';atlas_name=atlas.name
    target=n.new('ShaderNodeTexImage');target.image=atlas;target.name='Baked base pigment correction'
    for node in n:node.select=False
    target.select=True;n.active=target
    hidden={o:o.hide_render for o in s.objects if o.type=='MESH'}
    for ob in bpy.context.selected_objects:ob.select_set(False)
    for ob in hidden:ob.hide_render=ob not in objects
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=body;gpu(s);s.cycles.samples=1;s.render.bake.margin=6
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    baked=np.array(atlas.pixels[:],dtype=np.float32).reshape(2048,2048,4)
    # Cross and all upper-body texels are the exact accepted bytes. The lower
    # region is re-evaluated pigment, never a rendered beauty image.
    baked[:,1618:]=previous[:,1618:];baked[preserve_from_row:,:1618]=previous[preserve_from_row:,:1618]
    atlas.pixels.foreach_set(baked.reshape(-1));path=ROOT/cfg['texture'];path.parent.mkdir(parents=True,exist_ok=True);atlas.filepath_raw=str(path);atlas.file_format='PNG';atlas.save();atlas.pack()
    l.new(bs.outputs['BSDF'],outnode.inputs['Surface']);n.remove(emission)
    uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='Pigment atlas';l.new(uvnode.outputs[0],target.inputs['Vector']);l.new(target.outputs['Color'],bs.inputs['Base Color'])
    for ob,state in hidden.items():ob.hide_render=state
    regenerate(s)
    s['king_pigment_image']=atlas_name;s['king_pigment_atlas']=cfg['texture'];s['king_pigment_atlas_bakes_lighting']=False
    expected=np.array(atlas.pixels[:],dtype=np.float32);out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(out/'prepared.blend'),load_ui=False);actual=np.array(bpy.data.images[atlas_name].pixels[:],dtype=np.float32)
    error=float(abs(expected-actual).max());assert error<=1/255+.0001
    restored=actual.reshape(2048,2048,4);cross_error=float(abs(restored[:,1618:]-previous[:,1618:]).max());upper_error=float(abs(restored[preserve_from_row:,:1618]-previous[preserve_from_row:,:1618]).max());assert cross_error==upper_error==0
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest,atlas_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),packed_pixel_roundtrip_max_error=error,upper_body_preserved_from_row=preserve_from_row,cross_atlas_max_error=cross_error,upper_body_atlas_max_error=upper_error,atlas_bakes_lighting=False)
    run(rendercfg);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8')))
