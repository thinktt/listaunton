"""Isolated finish ablation: retain accepted pigment, geometry, camera and lights."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'models/rook/rook-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9eaaaaadfd2195591508cda798d56c27aa263ee3baa9424ded8acf76d6e4349c'
for label,rough,coat,coatrough,bump in [('007-polished',.16,.7,.06,True),('008-smooth-polish',.16,.7,.06,False),('009-smooth-baseline',.25,.35,.15,False)]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);mat=body.data.materials[0];nodes=mat.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Coat Weight'].default_value=coat;bs.inputs['Coat Roughness'].default_value=coatrough
    removed=[]
    if not bump:
        for name in ['Normal','Coat Normal']:
            for link in list(bs.inputs[name].links):removed.append([link.from_node.name,name]);mat.node_tree.links.remove(link)
    out=ROOT/'build/rook-mission'/label;out.mkdir(parents=True,exist_ok=True)
    s.cycles.samples=64;s.render.resolution_percentage=100;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'roughness':rough,'coat':coat,'coat_roughness':coatrough,'bump':bump,'removed_links':removed,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()},indent=2)+'\n')
    print('FINISH_ABLATION_DONE',label,flush=True)
