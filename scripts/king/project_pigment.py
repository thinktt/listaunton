"""Project derived pigment onto king surfaces; use real Principled BSDF lighting."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT, run, meshes

def prepare(cfg):
    source=ROOT/cfg['source'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;objects=meshes(scene);graph=bpy.context.evaluated_depsgraph_get()
    view=(scene.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    trees=[BVHTree.FromObject(ob,graph) for ob in objects]
    coverage={}
    for ob in objects:
        uv=ob.data.uv_layers.get('Reference pigment') or ob.data.uv_layers.new(name='Reference pigment')
        weights=[];coords=[]
        for v in ob.data.vertices:
            co=ob.matrix_world@v.co;p=world_to_camera_view(scene,scene.camera,co);coords.append((p.x,p.y))
            facing=max(0,min(1,(v.normal.dot(view)-.02)/.25))
            distances=[]
            for tree in trees:
                loc,_,_,_=tree.ray_cast(co+view*10,-view,20)
                if loc is not None:distances.append((loc-co).dot(view))
            visible=distances and max(distances)<.065
            weights.append(facing if visible else 0)
        for loop in ob.data.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
        attr=ob.data.attributes.get('Pigment coverage')
        if attr:ob.data.attributes.remove(attr)
        if 'cross' in ob.name:
            # Flat cross faces need face coverage; occluded bottom control vertices
            # must not interpolate a bare patch across the visible entire cross.
            attr=ob.data.attributes.new(name='Pigment coverage',type='FLOAT',domain='CORNER')
            for face in ob.data.polygons:
                facing=max(0,min(1,(face.normal.dot(view)-.01)/.2))
                for li in face.loop_indices:attr.data[li].value=facing
        else:
            attr=ob.data.attributes.new(name='Pigment coverage',type='FLOAT',domain='POINT')
            attr.data.foreach_set('value',weights)
        coverage[ob.name]={'vertices':len(weights),'covered':sum(w>.5 for w in weights)}
    mat=objects[0].data.materials[0].copy();mat.name='King walnut - generated diffuse pigment and live reflections'
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
    previous=bs.inputs['Base Color'].links[0].from_socket
    tex=n.new('ShaderNodeTexImage');tex.name='Derived king pigment';tex.image=bpy.data.images.load(str(ROOT/cfg['texture']),check_existing=False);tex.image.pack();tex.extension='EXTEND'
    uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='Reference pigment';l.new(uvnode.outputs[0],tex.inputs['Vector'])
    grade=n.new('ShaderNodeHueSaturation');grade.name='Pigment grade';grade.inputs['Value'].default_value=cfg.get('value',.7);grade.inputs['Saturation'].default_value=cfg.get('saturation',.9);l.new(tex.outputs['Color'],grade.inputs['Color'])
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='Pigment coverage'
    weight=n.new('ShaderNodeMath');weight.operation='MULTIPLY';l.new(attr.outputs['Fac'],weight.inputs[0]);l.new(tex.outputs['Alpha'],weight.inputs[1])
    mix=n.new('ShaderNodeMixRGB');mix.name='Continuous pigment';l.new(weight.outputs[0],mix.inputs[0]);l.new(previous,mix.inputs[1]);l.new(grade.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    # Fine pigment relief remains physically shallow; varnish is a separate layer.
    gray=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],gray.inputs[0])
    bump=n.new('ShaderNodeBump');bump.name='Pigment microrelief';bump.inputs['Strength'].default_value=cfg.get('relief_strength',.11);bump.inputs['Distance'].default_value=cfg.get('relief_distance',.003)
    l.new(gray.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value=cfg.get('roughness',.31);bs.inputs['Coat Weight'].default_value=cfg.get('coat',.3);bs.inputs['Coat Roughness'].default_value=cfg.get('coat_roughness',.2)
    for ob in objects:ob.data.materials[0]=mat
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k not in ['source_sha256','procedural']}
    rendercfg.update(source=str((out/'prepared.blend').relative_to(ROOT)),original_source=cfg['source'],original_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),coverage=coverage,texture_sha256=hashlib.sha256((ROOT/cfg['texture']).read_bytes()).hexdigest())
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);prepare(json.loads(Path(args.config).read_text(encoding='utf-8')))
