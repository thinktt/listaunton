"""Continue the visible king pigment onto unseen surfaces without baking light.

The hidden finish is an explicitly inferred reflection of the visible finish.
Original visible UVs, coverage, geometry, lighting and camera stay unchanged.
Run in Blender with -- CONFIG, from the tracked pre-atlas checkpoint source.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;objects=meshes(s)
    view=s.camera.matrix_world.to_3x3()@Vector((0,0,1))
    toward=Vector((view.x,view.y,0)).normalized()
    for ob in objects:
        layer=ob.data.uv_layers.get('Inferred hidden pigment') or ob.data.uv_layers.new(name='Inferred hidden pigment')
        coords=[]
        for v in ob.data.vertices:
            co=ob.matrix_world@v.co
            distance=co.dot(toward)
            if distance<0:co-=2*distance*toward
            p=world_to_camera_view(s,s.camera,co);coords.append((p.x,p.y))
        for loop in ob.data.loops:layer.data[loop.index].uv=coords[loop.vertex_index]
    mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    mix=n['Continuous pigment'];bump=n['Pigment microrelief'];copies={}
    def clone_socket(socket):
        original=socket.node;key=original.as_pointer()
        if key not in copies:
            copy=n.new(original.bl_idname);copies[key]=copy;copy.name='Inferred hidden / '+original.name
            for prop in ['operation','use_clamp','blend_type','interpolation','projection','extension','image','uv_map']:
                if hasattr(original,prop):setattr(copy,prop,getattr(original,prop))
            if copy.bl_idname=='ShaderNodeUVMap':copy.uv_map='Inferred hidden pigment'
            for i,inp in enumerate(original.inputs):
                if hasattr(inp,'default_value'):
                    value=inp.default_value
                    copy.inputs[i].default_value=list(value) if hasattr(value,'__len__') and not isinstance(value,str) else value
                if inp.is_linked:l.new(clone_socket(inp.links[0].from_socket),copy.inputs[i])
        idx=list(original.outputs).index(socket)
        return copies[key].outputs[idx]
    inferred_color=clone_socket(mix.inputs[2].links[0].from_socket)
    l.new(inferred_color,mix.inputs[1])
    actual_relief=bump.inputs['Height'].links[0].from_socket
    inferred_relief=clone_socket(actual_relief)
    relief=n.new('ShaderNodeMixRGB');relief.name='Continuous fine relief'
    l.new(mix.inputs[0].links[0].from_socket,relief.inputs[0]);l.new(inferred_relief,relief.inputs[1]);l.new(actual_relief,relief.inputs[2]);l.new(relief.outputs[0],bump.inputs['Height'])
    s['king_hidden_pigment']='Inferred mirrored visible diffuse pigment; actual coverage retains original projection.'
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'}
    rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=cfg['source'],original_source_sha256=digest,inferred_hidden_nodes=len(copies),inference='Reflect hidden surface toward camera in horizontal plane and reuse diffuse pigment/fine relief; no copied beauty lighting.')
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
