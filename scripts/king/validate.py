"""Validate the saved king's closed components, camera, packed pigment and export."""
import bpy,bmesh,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/king/king-rebuilt.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(model)
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);scene=bpy.context.scene;graph=bpy.context.evaluated_depsgraph_get();components=[]
for ob in scene.objects:
    if ob.type!='MESH' or ob.hide_render:continue
    ev=ob.evaluated_get(graph);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=graph);bm=bmesh.new();bm.from_mesh(me)
    count=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
    assert count==0 and volume>0,(ob.name,count,volume)
    assert all(math.isfinite(x) for v in me.vertices for x in v.co)
    uv=me.uv_layers.get('Pigment atlas');assert uv and all(math.isfinite(x) for row in uv.data for x in row.uv)
    components.append({'name':ob.name,'nonmanifold_edges':count,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
    bm.free();ev.to_mesh_clear()
    mat=ob.data.materials[0];output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
    assert output.inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED','Beauty material must be a real BSDF'
assert len(components)==2
meta=json.loads((root/'assets/king/mesh.json').read_text());assert meta['sourceSha256']==before
assert sha(root/meta['texture'])==meta['textureSha256']
atlas=bpy.data.images[scene.get('king_pigment_image','King pigment atlas')];assert atlas.packed_file
assert hashlib.sha256(bytes(atlas.packed_file.data)).hexdigest()==meta['textureSha256']
cam=scene.camera;axis=cam.matrix_world.to_3x3()@Vector((0,0,1));elevation=math.degrees(math.asin(axis.z))
assert cam.data.type=='ORTHO' and abs(elevation-54)<.001
actual=[float(v) for row in cam.matrix_world.inverted() for v in row]
assert max(abs(a-b) for a,b in zip(actual,meta['referenceCamera']['worldToCamera']))<1e-7
report=json.loads((root/'assets/king/validation.json').read_text());assert report['sourceSha256']==before
report.update(components=components,cameraMatchesExport=True,packedPigmentPngHashMatches=True,realPrincipledBeautyMaterial=True,sourceUnchanged=sha(model)==before,elevationDegrees=elevation)
(root/'assets/king/validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2));print('KING_VALIDATION_PASS')
