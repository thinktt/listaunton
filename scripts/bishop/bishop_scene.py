"""Select editable controls separately from optional derived render surfaces."""
def editable_meshes(scene):
    meshes=[o for o in scene.objects if o.type=='MESH' and not o.get('bishop_render_region')
            and (o.get('bishop_editable_control') or not o.hide_render)]
    assert len(meshes)==2,'Expected the closed turned body and button controls.'
    return meshes

def render_meshes(scene):
    return [o for o in scene.objects if o.type=='MESH' and not o.hide_render]
