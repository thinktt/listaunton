"""Diagnostic only: distinguish baked pigment brightness from real reflections."""
from pathlib import Path
import sys,bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'models/rook/rook-rebuilt.blend'
for variant,emission in [('015-diffuse-diagnostic',False),('016-pigment-diagnostic',True)]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);mat=body.data.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    if emission:
        pigment=bs.inputs['Base Color'].links[0].from_socket;em=mat.node_tree.nodes.new('ShaderNodeEmission');mat.node_tree.links.new(pigment,em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],mat.node_tree.nodes.get('Material Output').inputs['Surface'])
    else:
        bs.inputs['Coat Weight'].default_value=0;bs.inputs['Specular IOR Level'].default_value=0
    out=ROOT/'build/rook-mission'/variant;out.mkdir(parents=True,exist_ok=True);s.cycles.samples=32;s.render.filepath=str(out/'wood.png');bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'diagnostic_only':True,'emission':emission,'note':'Never eligible for final material promotion. No saved replacement model.'},indent=2)+'\n');print('PIGMENT_DIAGNOSTIC_DONE',variant,flush=True)
