"""Keep editable Boolean cut surfaces wooden without degenerate lathe UVs."""
def assign_cut_material(scene):
    import bpy
    import json
    body=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render and 'continuous' in o.name)
    base=body.data.materials[0];cut=base.copy();cut.name='Bishop boxwood — interior cut'
    nodes=cut.node_tree.nodes;links=cut.node_tree.links;bs=nodes['Principled BSDF']
    pigment=nodes['Hidden boxwood pigment'].outputs['Color']
    balance=json.loads(scene.get('bishop_diffuse_balance','{}')).get('starting_pigment_factor',1)
    if balance!=1:
        scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.name='Cut pigment energy balance';scale.inputs['Scale'].default_value=balance
        links.new(pigment,scale.inputs[0]);pigment=scale.outputs[0]
    links.new(pigment,bs.inputs['Base Color'])
    links.new(nodes['Fine wood pores'].outputs['Fac'],nodes['Wood micro relief'].inputs['Height'])
    nodes['Wood micro relief'].inputs['Distance'].default_value=.002
    bs.inputs['Roughness'].default_value=.32;bs.inputs['Coat Weight'].default_value=.2
    if len(body.data.materials)>1:body.data.materials[1]=cut
    else:body.data.materials.append(cut)
    modifier=next(m for m in body.modifiers if m.type=='BOOLEAN');cutter=modifier.object
    cutter.data.materials.clear();cutter.data.materials.append(base);cutter.data.materials.append(cut)
    for poly in cutter.data.polygons:poly.material_index=1
    if hasattr(modifier,'material_mode'):modifier.material_mode='INDEX'
    scene['bishop_cut_material']='Procedural boxwood on Boolean interior faces, whose lathe UVs are degenerate.'
    return cut
