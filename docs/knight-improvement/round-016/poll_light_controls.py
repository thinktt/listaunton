"""Identify the studio reflections on the upper mane without modifying the saved knight."""
import hashlib,json,sys
from pathlib import Path
import bpy
root,model,out=[Path(x).resolve() for x in sys.argv[sys.argv.index('--')+1:]]
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import configure_render,render,visible_meshes
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(model);bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene;configure_render(s,48)
s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=239/1254;s.render.border_max_x=508/1254
s.render.border_min_y=1-414/1254;s.render.border_max_y=1-278/1254
out.mkdir(parents=True,exist_ok=True)
managed={'key':'Poll flag | Walnut key','fill':'Poll flag | Walnut soft fill','upper strip':'Poll flag | Walnut upper strip','rear oval':'Walnut | poll rear oval'}
assert all(name in s.objects for name in managed.values())
lamps={k:s.objects[v] for k,v in managed.items()}
report={}
def frame(label):
    dest=out/(label+'.png');render(s,dest);report[label]=sha(dest)
frame('studio')
for label,lamp in lamps.items():
    lamp.hide_render=True
    frame('without-'+label.replace(' ','-'))
    lamp.hide_render=False
for lamp in lamps.values():lamp.hide_render=True
frame('without-all-four')
for lamp in lamps.values():lamp.hide_render=False
mats={slot.material for obj in visible_meshes(s) for slot in obj.material_slots if slot.material}
node_types={}
for mat in mats:
    node_types[mat.name]=[node.bl_idname for node in mat.node_tree.nodes if node.type in ('BSDF_PRINCIPLED','BSDF_GLOSSY','MIX_SHADER','ADD_SHADER','OUTPUT_MATERIAL')]
    for bs in mat.node_tree.nodes:
        if bs.type!='BSDF_PRINCIPLED':continue
        for k in ('Coat Weight','Specular IOR Level','Metallic'):
            socket=bs.inputs[k]
            for link in list(socket.links):mat.node_tree.links.remove(link)
            socket.default_value=0.0
frame('diffuse-control')
assert source==sha(model)
(out/'source.json').write_text(json.dumps({'model':source,'shots':report,'lights':{k:{'name':v.name,'energy':v.data.energy,'color':list(v.data.color)} for k,v in lamps.items()},'surface_nodes':node_types,'samples':48,'method':'Saved 54 degree studio and film gate, photographed with each of four mane lights disabled individually, all four disabled, and all lights present with Principled specular and coat strength set to zero. Each change occurs in memory. Compare visible sRGB changes at the same source pixels.'},indent=2)+'\n')
