"""Combine independently verified edits from the same knight, keeping one studio and atlas."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

def evaluated_digest(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    digest=hashlib.sha256()
    fields=[(mesh.vertices,'co',3,'f'),(mesh.edges,'vertices',2,'i'),
            (mesh.loops,'vertex_index',1,'i'),(mesh.corner_normals,'vector',3,'f')]
    for layer in mesh.uv_layers:
        fields.append((layer.data,'uv',2,'f'))
    for collection,prop,cols,dtype in fields:
        buf=np.empty(len(collection)*cols,dtype);collection.foreach_get(prop,buf);digest.update(buf.tobytes())
    ev.to_mesh_clear();digest.update(np.asarray(obj.matrix_world,dtype='f').tobytes())
    return digest.hexdigest()

def load(scene_file):
    bpy.ops.wm.open_mainfile(filepath=str(scene_file),load_ui=False)
    return bpy.context.scene

def state(scene, names):
    xyz={}; evaluated={}
    for name in names:
        obj=scene.objects[name]
        xyz[name]=np.empty(len(obj.data.vertices)*3,'f')
        obj.data.vertices.foreach_get('co',xyz[name])
        evaluated[name]=evaluated_digest(obj)
    return xyz,evaluated

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('recipe',type=Path)
    p.add_argument('out',type=Path);p.add_argument('--samples',type=int,default=144)
    p.add_argument('--preview',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.root.resolve();out=a.out.resolve()
    cfg=json.loads(a.recipe.read_bytes());out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/'scripts/knight'))
    from mission_scene import ASSETS,configure_render,json_file,save_model,render,sha,use_side_camera,visible_meshes
    from export_mission import export
    surf={}
    expected={}
    for source in cfg['components']:
        path=root/source['path']
        assert sha(path)==source['sha256']
        xyz,ev=state(load(path),source['objects'])
        assert not (set(surf)&set(xyz))
        surf.update(xyz);expected.update(ev)
    foundation=root/cfg['foundation']['path'];assert sha(foundation)==cfg['foundation']['sha256']
    scene=load(foundation)
    baseline={ob.name:evaluated_digest(ob) for ob in scene.objects if ob.type=='MESH'}
    for name,vertices in surf.items():
        ob=scene.objects[name]
        assert vertices.size==len(ob.data.vertices)*3
        ob.data.vertices.foreach_set('co',vertices);ob.data.update()
    bpy.context.view_layer.update()
    tex=root/cfg['texture']['path'];assert sha(tex)==cfg['texture']['sha256']
    if 'previous_sha256' in cfg['texture']:
        mat=visible_meshes(scene)[0].data.materials[0]
        node=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
        old=node.image
        assert hashlib.sha256(bytes(old.packed_file.data)).hexdigest()==cfg['texture']['previous_sha256']
        raw=tex.read_bytes()
        image=bpy.data.images.load(str(tex),check_existing=False)
        image.colorspace_settings.name='sRGB'
        image.name='Knight | walnut and turned platform'
        image.pack(data=raw,data_len=len(raw));node.image=image
        if old.users==0:bpy.data.images.remove(old)
    configure_render(scene,144);save_model(scene,out/'knight.blend');scene=load(out/'knight.blend')
    checked={ob.name:evaluated_digest(ob) for ob in scene.objects if ob.type=='MESH'}
    assert checked=={**baseline,**expected},'Merged coordinates, normals, topology, UVs or transforms differ from the selected individual carvings'
    mat=visible_meshes(scene)[0].data.materials[0]
    packed=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    assert bytes(packed.packed_file.data)==tex.read_bytes()
    meta=export(scene,tex,output=out,source=out/'knight.blend')
    configure_render(scene,a.samples)
    if a.preview:scene.render.resolution_percentage=66
    render(scene,out/'wood.png');use_side_camera(scene);render(scene,out/'wood-side.png')
    if not a.preview:
        for ob in visible_meshes(scene):ob.data.materials[0]=bpy.data.materials['Neutral satin clay']
        render(scene,out/'clay-side.png')
        scene=load(out/'knight.blend');configure_render(scene,a.samples)
        for ob in visible_meshes(scene):ob.data.materials[0]=bpy.data.materials['Neutral satin clay']
        render(scene,out/'clay-fixed.png')
    json_file(out/'combination.json',{'source_sha256':sha(out/'knight.blend'),'inputs':cfg,
             'geometry_sha256_by_part':checked,'texture_sha256':sha(tex),'camera':meta['referenceCamera'],
             'samples':a.samples,'preview':a.preview,'render_sha256':sha(out/'wood.png'),'side_sha256':sha(out/'wood-side.png')})
    print('COMBINATION_VERIFIED',sha(out/'knight.blend'))
if __name__=='__main__':main()
