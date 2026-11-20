from pathlib import Path
import argparse,json,hashlib,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT as R,gpu
from render_regions import controls
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=R/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
O=R/a.output;O.mkdir(parents=True,exist_ok=True)
w=s.render.resolution_x;h=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=350/w;s.render.border_max_x=660/w;s.render.border_min_y=1-470/h;s.render.border_max_y=1-370/h
mat=controls(s)[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF']
geo=n.new('ShaderNodeNewGeometry')
for label,inputs in [('smooth-coat',['Coat Normal']),('smooth-both',['Normal','Coat Normal'])]:
 for name in inputs:l.new(geo.outputs['Normal'],bs.inputs[name])
 s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(O/'diagnostic.json').write_text(json.dumps(dict(source=str(source),sha256=digest,note='Read-only normal-field diagnostic, never a final material or source modification.'),indent=2)+'\n',encoding='utf-8')
print('UPPER_NORMAL_DIAGNOSTIC_COMPLETE')
