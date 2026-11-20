"""Apply a replayable component finish to the model and check both real camera views."""
import sys
from pathlib import Path
import bpy

def main():
    root, source, mane, pigment, out = (Path(s).resolve() for s in sys.argv[-5:])
    sys.path.insert(0, str(root / 'scripts/knight'))
    sys.path.insert(0, str(mane))
    from apply_component import apply
    from mission_scene import configure_render, render, save_model, sha, use_side_camera, json_file
    from export_mission import export
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    assert sha(source) == '11d21ea5a6ff2200290da4dabd92a9aea63c087c8e670511a839ac371b48d108'
    scene = bpy.context.scene
    apply(scene, mane)
    powers = {}
    for side, scale in [('left', .50), ('right', .30)]:
        obj = scene.objects[f'Walnut | {side} collar strip']
        assert [other.name for other in obj.light_linking.receiver_collection.all_objects] == ['Knight | turned pedestal']
        before = obj.data.energy
        obj.data.energy *= scale
        powers[side] = [before, obj.data.energy]
    out.mkdir(parents=True, exist_ok=True)
    configure_render(scene, 144)
    save_model(scene, out / 'knight.blend')
    bpy.ops.wm.open_mainfile(filepath=str(out / 'knight.blend'), load_ui=False)
    scene = bpy.context.scene
    export(scene, pigment, output=out, source=out/'knight.blend')
    render(scene, out / 'wood.png')
    use_side_camera(scene)
    render(scene, out / 'wood-side.png')
    json_file(out/'finish.json', {'parent':sha(source), 'model':sha(out/'knight.blend'), 'powers':powers,
              'fixed':sha(out/'wood.png'), 'profile':sha(out/'wood-side.png'), 'mane_recipe':sha(mane/'recipe.json')})
if __name__=='__main__':main()
