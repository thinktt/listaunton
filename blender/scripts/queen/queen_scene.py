"""Distinguish the editable queen surface from optional light-link receivers."""
def editable_mesh(scene):
    marked=[o for o in scene.objects if o.type=='MESH' and o.get('mission_editable_control')]
    if marked:
        assert len(marked)==1
        return marked[0]
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    assert len(visible)==1
    return visible[0]

def render_meshes(scene):
    receivers=[o for o in scene.objects if o.type=='MESH' and o.get('mission_render_region')]
    return receivers or [editable_mesh(scene)]

def set_material(scene,material):
    for obj in [editable_mesh(scene)]+render_meshes(scene):
        obj.data.materials[0]=material
