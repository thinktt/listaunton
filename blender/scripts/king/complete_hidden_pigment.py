"""Complete unseen turned wood from the accepted material, retaining its front.

This is material inference, not additional source evidence. The fixed camera,
closed geometry, accepted UVs, relief and live lights are not changed. Coverage
and grazing modes retain the central front but may change its edge pigment.
"""
from pathlib import Path
import argparse, hashlib, json, math, sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT, gpu, run
from render_regions import controls, regenerate
from validate_render_regions import check

def main(cfg):
    source=ROOT/cfg['source'];source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    assert source_hash==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;obs=controls(s);body=next(o for o in obs if 'body' in o.name)
    graph=bpy.context.evaluated_depsgraph_get()
    trees=[(o,BVHTree.FromObject(o,graph)) for o in obs]
    view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    visible=[]
    for v in body.data.vertices:
        co=body.matrix_world@v.co;distances=[]
        for ob,tree in trees:
            inv=ob.matrix_world.inverted();p,_,_,_=tree.ray_cast(inv@(co+view*10),(inv.to_3x3()@(-view)).normalized(),20)
            if p is not None:distances.append((ob.matrix_world@p-co).dot(view))
        visible.append(v.normal.dot(view)>-.04 and bool(distances) and max(distances)<.035)
    visible=np.array(visible).reshape(-1,96)
    hidden=(~visible).astype(np.float32)
    if cfg.get('mask_mode')=='coverage':
        coverage=np.array([a.value for a in body.data.attributes['Pigment coverage'].data],dtype=np.float32).reshape(-1,96)
        hidden=np.clip((.98-coverage)/.50,0,1)
        visible=coverage>=.98
    if cfg.get('grazing_blend'):
        co=np.array([v.co[:] for v in body.data.vertices]);normals=np.array([v.normal[:] for v in body.data.vertices]);r=np.maximum(np.linalg.norm(co[:,:2],axis=1),1e-8)
        angle=np.degrees(np.arccos(np.clip(-co[:,1]/r,-1,1)))
        start,end=cfg['grazing_blend'];t=np.clip((angle-start)/(end-start),0,1)
        grazing=t*t*(3-2*t)*np.clip((.84-normals@np.array(view))/.60,0,1)
        hidden=np.maximum(hidden,grazing.reshape(hidden.shape));visible=hidden<1e-6
    # Broaden the retained region; all visible control vertices stay exactly zero.
    for _ in range(cfg.get('feather_steps',20)):
        h=(hidden*2+np.roll(hidden,1,1)+np.roll(hidden,-1,1)+np.vstack([hidden[:1],hidden[:-1]])+np.vstack([hidden[1:],hidden[-1:]]))/6
        hidden=np.where(visible,0,h)
    hidden=np.clip(hidden,0,1)
    for ob in obs:
        attr=ob.data.attributes.get('Hidden pigment inference') or ob.data.attributes.new('Hidden pigment inference','FLOAT','POINT')
        attr.data.foreach_set('value',hidden.reshape(-1) if ob==body else np.zeros(len(ob.data.vertices)))
        original=ob.data.uv_layers['Pigment atlas']
        folded=ob.data.uv_layers.get('Hidden pigment sample') or ob.data.uv_layers.new(name='Hidden pigment sample')
        for loop in ob.data.loops:
            u,v=original.data[loop.index].uv
            if ob==body:
                t=(u-.01)/.77
                angle=(t-.5)*2*math.pi
                if cfg.get('sample_mode')=='generated_tile':
                    folded.data[loop.index].uv=(t*cfg.get('tile_u_scale',1.0),(v-.01)/.98*cfg.get('tile_v_scale',1.0))
                    continue
                elif cfg.get('sample_mode')=='right_strip':
                    folded_t=cfg.get('sample_center',.63)+cfg.get('sample_amplitude',.07)*math.cos(2*math.pi*t)
                else:folded_t=.5+cfg.get('sample_width',.72)*math.asin(math.sin(angle))/(2*math.pi)
                u=.01+.77*folded_t
            folded.data[loop.index].uv=(u,v)
        ob.data.uv_layers.active=original;original.active_render=True
    mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF']
    old=bpy.data.images[s['king_pigment_image']];assert not old.is_float
    size=tuple(old.size);assert size==(2048,2048)
    previous=np.array(old.pixels[:],dtype=np.float32).reshape(2048,2048,4)
    oldcolor=bs.inputs['Base Color'].links[0].from_socket
    uvnode=n.new('ShaderNodeUVMap');uvnode.name='Inferred hidden wood coordinates';uvnode.uv_map='Hidden pigment sample'
    sampled=n.new('ShaderNodeTexImage');sampled.name='Hidden turned wood sample';sampled.image=old;sampled.extension='EXTEND';l.new(uvnode.outputs[0],sampled.inputs['Vector'])
    if cfg.get('sample_mode')=='generated_tile':
        if cfg.get('generated_source_sha256'):assert hashlib.sha256((ROOT/cfg['generated_source']).read_bytes()).hexdigest()==cfg['generated_source_sha256']
        tile=bpy.data.images.load(str(ROOT/cfg['generated_source']),check_existing=False);tile.pack();sampled.image=tile;sampled.extension='REPEAT'
    inferred=sampled.outputs['Color']
    if cfg.get('sample_grade'):
        grade=n.new('ShaderNodeHueSaturation');grade.name='Inferred wood grade';grade.inputs['Value'].default_value=cfg['sample_grade'];l.new(inferred,grade.inputs['Color']);inferred=grade.outputs['Color']
    attrnode=n.new('ShaderNodeAttribute');attrnode.attribute_name='Hidden pigment inference'
    mix=n.new('ShaderNodeMixRGB');mix.name='Continuous unseen wood';l.new(attrnode.outputs['Fac'],mix.inputs[0]);l.new(oldcolor,mix.inputs[1]);l.new(inferred,mix.inputs[2])
    output=next(x for x in n if x.type=='OUTPUT_MATERIAL')
    emission=n.new('ShaderNodeEmission');l.new(emission.outputs[0],output.inputs['Surface'])
    target=n.new('ShaderNodeTexImage');target.name='Completed king pigment atlas'
    hidden_states={o:o.hide_render for o in s.objects if o.type=='MESH'}
    for ob in bpy.context.selected_objects:ob.select_set(False)
    for ob in hidden_states:ob.hide_render=ob not in obs
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=body;gpu(s);s.cycles.samples=1;s.render.bake.margin=6
    for node in n:node.select=False
    target.select=True;n.active=target
    mask=bpy.data.images.new('King inferred hidden pigment mask',width=2048,height=2048,alpha=False,float_buffer=True)
    mask.colorspace_settings.name='Non-Color';target.image=mask;l.new(attrnode.outputs['Fac'],emission.inputs['Color'])
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    weights=np.array(mask.pixels[:],dtype=np.float32).reshape(2048,2048,4)[:,:,0]
    atlas=bpy.data.images.new('King completed pigment '+Path(cfg['texture']).stem,width=2048,height=2048,alpha=False)
    atlas.colorspace_settings.name='sRGB';target.image=atlas;l.new(mix.outputs[0],emission.inputs['Color'])
    bpy.ops.object.bake(type='EMIT',use_clear=True)
    baked=np.array(atlas.pixels[:],dtype=np.float32).reshape(2048,2048,4)
    # Retain exact pigment bytes outside the inferred hidden surface. Cross
    # islands are protected even if the bake's padding reaches their boundary.
    preserve=weights<1e-5;preserve[:,1618:]=True;baked[preserve]=previous[preserve]
    atlas.pixels.foreach_set(baked.reshape(-1));path=ROOT/cfg['texture'];path.parent.mkdir(parents=True,exist_ok=True)
    atlas.filepath_raw=str(path);atlas.file_format='PNG';atlas.save();atlas.pack()
    l.new(bs.outputs['BSDF'],output.inputs['Surface']);n.remove(emission)
    final_uv=n.new('ShaderNodeUVMap');final_uv.uv_map='Pigment atlas';l.new(final_uv.outputs[0],target.inputs['Vector']);l.new(target.outputs['Color'],bs.inputs['Base Color'])
    if cfg.get('cleanup'):
        for temp in [uvnode,sampled,attrnode,mix]+([grade] if cfg.get('sample_grade') else []):n.remove(temp)
        for ob in obs:
            ob.data.uv_layers.remove(ob.data.uv_layers['Hidden pigment sample'])
            ob.data.attributes.remove(ob.data.attributes['Hidden pigment inference'])
            ob.data.uv_layers.active=ob.data.uv_layers['Pigment atlas'];ob.data.uv_layers.active.active_render=True
        bpy.data.images.remove(mask)
    for ob,state in hidden_states.items():ob.hide_render=state
    regenerate(s);regions=check(s)
    s['king_pigment_image']=atlas.name;s['king_pigment_atlas']=cfg['texture'];s['king_pigment_atlas_bakes_lighting']=False
    s['king_hidden_pigment_method']=json.dumps(dict(mask=cfg.get('mask_mode','visibility'),source=cfg.get('sample_mode','folded'),grazing=cfg.get('grazing_blend'),note='Central front pigment retained; unseen finish inferred, not additional historical evidence. Edge texels can change in coverage/grazing modes.'))
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/'completion-mask.npz',weights=weights,preserved=preserve)
    report={'source_sha256':source_hash,'source_atlas':old.name,'preserved_texels':int(preserve.sum()),'total_texels':int(preserve.size),'cross_pixels_identical':bool(np.array_equal(baked[:,1618:],previous[:,1618:])),'changed_texels':int(np.any(baked!=previous,2).sum()),'geometry_camera_lights_unchanged_by_construction':True,'receiver_check':regions,'inferred_not_observed':True,'temporary_uvs_attributes_removed':bool(cfg.get('cleanup')),'generated_source_sha256':hashlib.sha256((ROOT/cfg['generated_source']).read_bytes()).hexdigest() if cfg.get('generated_source') else None}
    expected=np.array(atlas.pixels[:],dtype=np.float32);atlas_name=atlas.name
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(out/'prepared.blend'),load_ui=False)
    actual=np.array(bpy.data.images[atlas_name].pixels[:],dtype=np.float32)
    report['packed_roundtrip_max_error']=float(abs(expected-actual).max());assert report['packed_roundtrip_max_error']==0
    (out/'completion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=source_hash)
    run(rendercfg);assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
