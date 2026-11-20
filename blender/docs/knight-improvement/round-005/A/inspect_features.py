"""Matched clay studies and topology checks on reopened candidate and parent."""
from pathlib import Path
import hashlib
import sys
import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'scripts/knight'));sys.path.insert(0,str(OUT))
from mission_scene import configure_render,json_file,render,sha,use_side_camera,visible_meshes
from diagnostic_views import clay_studio,orbit
from probe_carving import point_probe


def report(scene):
    result={}
    for obj in visible_meshes(scene):
        mesh=obj.data
        bm=bmesh.new();bm.from_mesh(mesh)
        off=sum(not e.is_manifold for e in bm.edges)
        deg=sum(f.calc_area()<1e-11 for f in bm.faces)
        bm.free()
        uv={}
        for layer in mesh.uv_layers:
            a=np.empty(len(layer.uv)*2,np.float32)
            layer.uv.foreach_get('vector',a)
            assert np.isfinite(a).all()
            uv[layer.name]={'count':len(a)//2,'min':float(a.min()),'max':float(a.max())}
        var=mesh.attributes['Knight varnish coverage']
        coverage=np.empty(len(var.data),np.float32);var.data.foreach_get('value',coverage)
        assert np.isfinite(coverage).all() and min(coverage)>=0 and max(coverage)<=1
        result[obj.name]={'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'nonmanifold_edges':off,
                          'faces_under_1e-11_area':deg,'uv':uv,'varnish_range':[float(coverage.min()),float(coverage.max())]}
    probe=point_probe(scene)
    visible=[]
    for y in range(443,514,2):
        for x in range(438,569,2):
            h=probe(x,y)
            if h and h[1].endswith('near eye'):visible.append([x,y])
    arr=np.array(visible)
    eye={'ray_samples':len(arr)}
    if len(arr):
        uv=arr-arr.mean(0);_,_,vt=np.linalg.svd(uv)
        line=vt[0]
        eye.update({'bounds':[arr.min(0).tolist(),arr.max(0).tolist()],'center':arr.mean(0).tolist(),
                    'downward_angle_deg':float(np.degrees(np.arctan(line[1]/line[0])))})
    return {'meshes':result,'eye':eye,'packed_images':{im.name:hashlib.sha256(im.packed_file.data).hexdigest()
        for im in bpy.data.images if im.packed_file},'lights':{o.name:[list(o.location),list(o.rotation_euler),
        o.data.energy,list(o.data.color),o.hide_render] for o in scene.objects if o.type=='LIGHT'}}


def light_settings(scene):
    return {o.name:{'position':list(o.location),'rotation':list(o.rotation_euler),'shape':o.data.shape,
            'size':o.data.size,'size_y':o.data.size_y,'spread':o.data.spread,'energy':o.data.energy,
            'receiver':o.light_linking.receiver_collection.name if o.light_linking.receiver_collection else None}
            for o in scene.objects if o.type=='LIGHT'}


def apply_studio(settings):
    for name,desc in settings.items():
        ob=bpy.data.objects[name]
        ob.location=desc['position'];ob.rotation_euler=desc['rotation']
        for key in ['shape','size','size_y','spread','energy']:setattr(ob.data,key,desc[key])
        ob.light_linking.receiver_collection=bpy.data.collections[desc['receiver']] if desc['receiver'] else None
    bpy.context.view_layer.update()


info={}
for label,fn in [('parent','parent.blend'),('candidate','knight.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(OUT/fn),load_ui=False)
    scene=bpy.context.scene
    info[label]=report(scene)
    info[label]['studio']=light_settings(scene)
    info[label]['scene_sha256']=sha(OUT/fn)
    json_file(OUT/'verified.json',info)
    if label=='parent' and all((OUT/f'parent-{k}-clay.png').exists() for k in
                              ['fixed','side','rear','rear-quarter','far-rear-quarter','front']):
        continue
    if label=='candidate':
        apply_studio(info['parent']['studio'])
        configure_render(scene,144);render(scene,OUT/'matched-parent-fixed.png')
        use_side_camera(scene);render(scene,OUT/'matched-parent-side.png')
        bpy.ops.wm.open_mainfile(filepath=str(OUT/fn),load_ui=False);scene=bpy.context.scene
    configure_render(scene,28);clay_studio(scene,10.3)
    render(scene,OUT/f'{label}-fixed-clay.png')
    use_side_camera(scene);render(scene,OUT/f'{label}-side-clay.png')
    scene.render.resolution_x=scene.render.resolution_y=640
    for name,az in [('rear',270),('rear-quarter',315),('far-rear-quarter',225),('front',90)]:
        orbit(scene,az+10.3,8,Vector((0,0,2.62)))
        render(scene,OUT/f'{label}-{name}-clay.png')
changes=[n for n,v in info['parent']['studio'].items() if v!=info['candidate']['studio'][n]]
assert set(changes)=={'Walnut | poll rear oval','Eye reflection upper','Eye reflection lower'}
assert info['parent']['packed_images']==info['candidate']['packed_images']
print('INSPECTED',info['candidate']['eye'],flush=True)
