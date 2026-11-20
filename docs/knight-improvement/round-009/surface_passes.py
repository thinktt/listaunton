"""Isolate pigment and polish on the knight's upper head in the saved 54° view."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('model',type=Path);p.add_argument('out',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from mission_scene import configure_render,render,visible_meshes
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=sha(a.model)
bpy.ops.wm.open_mainfile(filepath=str(a.model.resolve()),load_ui=False)
s=bpy.context.scene
lights={o.name:{'energy':o.data.energy,'type':o.data.type} for o in s.objects if o.type=='LIGHT' and not o.hide_render}
configure_render(s,32)
side=s.render.resolution_x
s.render.use_border=True
s.render.use_crop_to_border=False
s.render.border_min_x=190/side;s.render.border_max_x=770/side
s.render.border_min_y=1-570/side;s.render.border_max_y=1-261/side
objects=visible_meshes(s)
slots=[slot for obj in objects for slot in obj.material_slots if slot.material]
saved=[slot.material for slot in slots]
wood=set(saved)
a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
def modified(mat,kind):
    clone=mat.copy()
    bs=clone.node_tree.nodes.get('Principled BSDF')
    if not bs:raise ValueError(mat.name)
    links=clone.node_tree.links
    if kind=='pigment':
        pigment=bs.inputs['Base Color'].links[0].from_socket
        emission=clone.node_tree.nodes.new('ShaderNodeEmission')
        links.new(pigment,emission.inputs['Color'])
        output=next(n for n in clone.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        links.new(emission.outputs[0],output.inputs['Surface'])
    else:
        # Keep the real wood normals, coat, roughness and lamps. Replace
        # diffuse colour only, to retain the scene's exact specular behavior.
        for endpoint in clone.node_tree.nodes:
            if endpoint.type=='BSDF_PRINCIPLED':
                base=endpoint.inputs['Base Color']
                for link in list(base.links):links.remove(link)
                base.default_value=(.085,.085,.085,1)
    return clone
outputs={}
for kind in ('pigment','polish'):
    edits={mat:modified(mat,kind) for mat in wood}
    for slot,mat in zip(slots,saved):slot.material=edits[mat]
    destination=a.out/(kind+'.png');render(s,destination)
    outputs[kind]=sha(destination)
assert sha(a.model)==source
(a.out/'source.json').write_text(json.dumps({'source_sha256':source,'views':outputs,'lights':lights,'method':'At the saved 54-degree camera, full-res cropped film gate. Pigment routes the existing BSDF base-colour input directly to emission. Polish replaces that input with a neutral grey while leaving source normals, roughness, coat, lights and registration intact. Both passes use the scene colour transform.'},indent=2)+'\n')
