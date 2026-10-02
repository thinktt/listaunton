import bpy, bmesh, json, sys, argparse
from pathlib import Path

out=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20\outputs\queen-hires')
bpy.ops.wm.open_mainfile(filepath=str(out/'queen-rebuilt.blend'))
report={'meshes':[], 'reference_packed':False, 'camera_background':False}
depsgraph=bpy.context.evaluated_depsgraph_get()
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    ev=ob.evaluated_get(depsgraph)
    me=ev.to_mesh()
    bm=bmesh.new();bm.from_mesh(me)
    record={'name':ob.name,'editable_vertices':len(ob.data.vertices),
            'render_vertices':len(me.vertices),'render_faces':len(me.polygons),
            'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
            'loose_vertices':sum(not v.link_edges for v in bm.verts),
            'volume':bm.calc_volume(signed=True),
            'subdivision_editable':any(m.type=='SUBSURF' for m in ob.modifiers)}
    report['meshes'].append(record)
    assert record['non_manifold_edges']==0, record
    assert record['loose_vertices']==0, record
    assert record['volume']>0, record
    bm.free();ev.to_mesh_clear()
for im in bpy.data.images:
    if im.name.startswith('reference'): report['reference_packed']=bool(im.packed_file)
cam=bpy.context.scene.camera.data
report['camera_background']=cam.show_background_images and len(cam.background_images)>0
report['resolution']=[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y]
report['render_samples']=bpy.context.scene.cycles.samples
assert report['reference_packed'] and report['camera_background']
assert report['resolution']==[1254,1254]
parser=argparse.ArgumentParser()
parser.add_argument('--baseline',type=Path)
parser.add_argument('--expected-crown-z-shift',type=float,default=0.)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if args.baseline:
    crown=next(ob for ob in bpy.context.scene.objects if ob.name.startswith('02 Crown'))
    with bpy.data.libraries.load(str(args.baseline.resolve()),link=False) as (source,destination):
        destination.objects=[name for name in source.objects if name.startswith('02 Crown')]
    assert len(destination.objects)==1
    old=destination.objects[0]
    shape_unchanged=(len(crown.data.vertices)==len(old.data.vertices)
        and len(crown.data.polygons)==len(old.data.polygons)
        and all(tuple(a.co)==tuple(b.co) for a,b in zip(crown.data.vertices,old.data.vertices))
        and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(crown.data.polygons,old.data.polygons))
        and [(m.type,m.levels,m.render_levels) for m in crown.modifiers if m.type=='SUBSURF']
            ==[(m.type,m.levels,m.render_levels) for m in old.modifiers if m.type=='SUBSURF'])
    expected=old.matrix_basis.copy()
    expected.translation.z+=args.expected_crown_z_shift
    transform_matches=all(abs(crown.matrix_basis[r][c]-expected[r][c])<1e-7
                          for r in range(4) for c in range(4))
    report['approved_crown_unchanged']=shape_unchanged and crown.matrix_basis==old.matrix_basis
    report['approved_crown_shape_unchanged']=shape_unchanged
    report['expected_crown_z_shift']=args.expected_crown_z_shift
    report['crown_transform_matches_expected']=transform_matches
    assert shape_unchanged,'Approved crown shape was modified'
    assert transform_matches,'Crown transform differs from its expected translation'
    bpy.data.objects.remove(old,do_unlink=True)
report['passed']=True
(out/'model-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
