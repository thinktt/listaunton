"""Transfer the verified chest varnish and its four studio strips to the 008 carving."""
from hashlib import sha256
from pathlib import Path
import json
import bpy
import numpy as np
from mathutils import Matrix

def digest(array):
    return sha256(np.ascontiguousarray(array).tobytes()).hexdigest()

def apply(scene, directory=None, pigment=None):
    directory=Path(directory or Path(__file__).parent)
    recipe=json.loads((directory/'recipe.json').read_bytes())
    mesh=scene.objects[recipe['receiver']].data
    vertices=np.empty((len(mesh.vertices),3),'f')
    mesh.vertices.foreach_get('co',vertices.ravel())
    assert digest(vertices)==recipe['geometry_sha256'], 'The chest carving has changed.'
    surface=mesh.attributes['Knight varnish coverage']
    previous=np.empty(len(vertices),'f')
    surface.data.foreach_get('value',previous)
    assert digest(previous)==recipe['prior_coverage_sha256'], 'The chest finish has changed.'
    source=directory/'polish.npz'
    assert sha256(source.read_bytes()).hexdigest()==recipe['polish_file_sha256']
    parameters=np.load(source,allow_pickle=False)
    for key in ('varnish','flat_polish'):
        vals=parameters[key]
        assert len(vals)==len(vertices) and np.isfinite(vals).all() and vals.min()>=0 and vals.max()<=1
    mat=mesh.materials[0]
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    satin=nodes['Satin walnut in open grain']
    attrs=recipe['shader']
    assert 'Rubbed chest flats' not in mesh.attributes
    assert all(not satin.inputs[k].is_linked and abs(satin.inputs[k].default_value-v['rest'])<1e-6 for k,v in attrs.items())
    assert all(lamp['name'] not in scene.objects for lamp in recipe['cards'])
    receivers=bpy.data.collections[recipe['collection']]
    assert [ob.name for ob in receivers.all_objects]==[recipe['receiver']]
    color_node=nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
    old=color_node.image
    if pigment is not None:
        raw=Path(pigment).read_bytes()
        assert sha256(bytes(old.packed_file.data)).hexdigest()==recipe['parent_atlas']
        assert sha256(raw).hexdigest()==recipe['graded_atlas']
    surface.data.foreach_set('value',parameters['varnish'])
    flats=mesh.attributes.new('Rubbed chest flats','FLOAT','POINT')
    flats.data.foreach_set('value',parameters['flat_polish'])
    attr=nodes.new('ShaderNodeAttribute')
    attr.name='Chest | rubbed flats'
    attr.attribute_name=flats.name
    for name,val in attrs.items():
        scale=nodes.new('ShaderNodeMath')
        scale.name='Chest | satin '+name
        scale.operation='MULTIPLY_ADD'
        scale.inputs[1].default_value=val['scale']
        scale.inputs[2].default_value=val['rest']
        links.new(attr.outputs['Fac'],scale.inputs[0])
        links.new(scale.outputs[0],satin.inputs[name])
    for lamp in recipe['cards']:
        data=bpy.data.lights.new(lamp['name'],'AREA')
        data.shape='RECTANGLE'
        for field,value in lamp['data'].items():setattr(data,field,value)
        ob=bpy.data.objects.new(lamp['name'],data)
        scene.collection.objects.link(ob)
        ob.matrix_world=Matrix(lamp['matrix_world'])
        ob.visible_diffuse=False
        ob.visible_glossy=True
        ob.light_linking.receiver_collection=receivers
    if pigment is not None:
        image=bpy.data.images.load(str(Path(pigment).resolve()),check_existing=False)
        image.name='Knight | registered walnut pigment'
        image.colorspace_settings.name='sRGB'
        image.pack(data=raw,data_len=len(raw))
        color_node.image=image
        if old.users==0:bpy.data.images.remove(old)
    mesh.update()
    bpy.context.view_layer.update()
