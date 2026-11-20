"""Real, mane-linked oval softboxes and a less burnished upper mane."""
from pathlib import Path
import json
import math
import sys
import bpy
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'))
sys.path.insert(0,str(OUT))
from capture_material import read_pass
from fit_eye_reflection import display_transform
from mission_scene import configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes
from probe_carving import point_probe
from diagnostic_views import pictures

PARENT='709fb263f2cdf079c1a645002064ce83b72ff6b15faea2a9d8e8a19adfdd4dfb'
RECT=(268,282,496,386)
XS=[295,310,327,347,369,393,415,433,446,456,468]
YS=[348,343,340,338,338,338,339,341,344,349,356]
NOMINAL=95.


def reflectors(scene,mane):
    ev=mane.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    mesh.calc_loop_triangles()
    mat=np.asarray(mane.matrix_world)
    verts=np.array([tuple(v.co) for v in mesh.vertices])@mat[:3,:3].T+mat[:3,3]
    tri=np.array([list(t.vertices) for t in mesh.loop_triangles])
    ns=np.array([[list(mesh.corner_normals[k].vector) for k in t.loops] for t in mesh.loop_triangles])
    tree=BVHTree.FromPolygons(verts.tolist(),tri.tolist(),all_triangles=True)
    view=np.asarray(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    probe=point_probe(scene)
    hits=[]
    for x,y in zip(XS,YS):
        h=probe(x+.5,y+.5)
        if h[1]!=mane.name:
            continue
        q=np.asarray(h[2])
        _,_,i,_=tree.find_nearest(Vector(q))
        a,b,c=verts[tri[i]]
        u,v=np.linalg.lstsq(np.column_stack((b-a,c-a)),q-a,rcond=None)[0]
        normal=(np.array([1-u-v,u,v])@ns[i])@np.linalg.inv(mat[:3,:3])
        normal/=np.linalg.norm(normal)
        reflection=2*normal.dot(view)*normal-view
        hits.append((x,q,reflection))
    ev.to_mesh_clear()
    receiver=bpy.data.collections.new('Knight | mane studio receivers')
    receiver.objects.link(mane)
    lamps=[];inputs=[]
    # Two slightly overlapping elongated cards allow the bright edge to turn
    # towards the forehead. Their fixed world transforms also serve side views.
    for tag,lo,hi,width in [('rear',295,393,.064),('front',369,468,.060)]:
        entries=[h for h in hits if lo<=h[0]<=hi]
        points=np.array([h[1] for h in entries]); reflected=np.array([h[2] for h in entries])
        plane_n=reflected[len(entries)//2].copy()
        plane_pt=points[len(entries)//2]+1.50*plane_n
        d=((plane_pt-points)@plane_n)/(reflected@plane_n)
        positions=points+d[:,None]*reflected
        center=positions.mean(0)
        _,_,basis=np.linalg.svd(positions-center)
        along=basis[0];along-=plane_n*along.dot(plane_n);along/=np.linalg.norm(along)
        across=np.cross(plane_n,along)
        ext=(positions-center)@along
        center+=.5*(ext.max()+ext.min())*along
        light=bpy.data.lights.new('Walnut | poll '+tag+' oval','AREA')
        light.shape='ELLIPSE';light.size=float(np.ptp(ext))*1.22
        light.size_y=width;light.energy=0;light.color=(1,.91,.8)
        ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob)
        ob.location=Vector(center)
        ob.rotation_euler=Matrix(np.column_stack((along,across,plane_n)).tolist()).to_euler()
        ob.visible_diffuse=False;ob.visible_glossy=True;ob.light_linking.receiver_collection=receiver
        lamps.append(ob)
        inputs.append({'name':ob.name,'location':list(ob.location),'rotation':list(ob.rotation_euler),
                       'full_axes':[light.size,light.size_y],'alignment_pixels':[h[0] for h in entries],
                       'perpendicular_alignment_range':float(np.ptp((positions-center)@across))})
    return lamps,inputs


def configure_crop(scene):
    x0,y0,x1,y1=RECT
    configure_render(scene,384)
    scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.04)/1254;scene.render.border_max_x=(x1+.04)/1254
    scene.render.border_min_y=(1254-y1+.04)/1254;scene.render.border_max_y=(1254-y0+.04)/1254


def build():
    assert sha(OUT/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'parent.blend'),load_ui=False)
    scene=bpy.context.scene;mane=bpy.data.objects['Knight | swept rounded mane']
    attribute=mane.data.attributes['Knight varnish coverage']
    before=np.empty(len(attribute.data),np.float32);attribute.data.foreach_get('value',before)
    # Smooth, bilateral finish change by authored loft section, independent of
    # viewing direction, pixel coordinates, grain values and surface normals.
    weights=np.repeat(np.array([1,1,1,1,1,.76,.36,.06,0,0,0,0,0],np.float32),64)
    def apply_polish(factor):
        values=(before*(1-(1-factor)*weights)).astype(np.float32)
        attribute.data.foreach_set('value',values);mane.data.update()
        bpy.context.view_layer.update()
    configure_crop(scene)
    passes=OUT/'response';passes.mkdir(exist_ok=True)
    def take(name):return read_pass(scene,passes/(name+'.exr'))[:,:,:3].copy()
    parent=take('parent')
    contribution={}
    for name in ('Walnut key','Walnut soft fill','Walnut upper strip'):
        ob=bpy.data.objects[name];ob.visible_glossy=False
        minus=take(name.replace(' ','-')+'-without-gloss')
        ob.visible_glossy=True
        contribution[name]=float(np.maximum(0,parent-minus).mean())
    lamps,inputs=reflectors(scene,mane)
    # Basis renders measure true multi-bounce Cycles response. The candidate
    # is fitted only in actual lamp wattages and one material coverage value.
    endpoint=.16
    # The other six parts retain the original main lights. These copies have
    # identical transforms and dimensions and act as flags on the mane only.
    other=bpy.data.collections.new('Knight | studio receivers beside mane')
    for ob in visible_meshes(scene):
        if ob!=mane:other.objects.link(ob)
    flags=[]
    for name in ('Walnut key','Walnut soft fill','Walnut upper strip'):
        original=bpy.data.objects[name]
        assert original.light_linking.receiver_collection is None
        duplicate=original.copy()
        duplicate.data=original.data.copy()
        duplicate.name='Poll flag | '+name
        scene.collection.objects.link(duplicate)
        duplicate.light_linking.receiver_collection=lamps[0].light_linking.receiver_collection
        original.light_linking.receiver_collection=other
        flags.append(duplicate)
    def set_flags(scale):
        for ob in flags:
            name=ob.name.removeprefix('Poll flag | ')
            ob.data.energy=bpy.data.objects[name].data.energy*scale
    captured=[]
    for j,factor in enumerate((endpoint,1.0)):
        apply_polish(factor)
        set_flags(0.55)
        base=take(f'polish-{j}-low')
        set_flags(1)
        high=take(f'polish-{j}')
        responses=[]
        for i,lamp in enumerate(lamps):
            lamp.data.energy=NOMINAL
            response=take(f'polish-{j}-oval-{i}')
            lamp.data.energy=0
            responses.append(response-high)
        captured.append(np.stack([base,(high-base)/.45,*responses]))
    np.save(OUT/'responses-linear.npy',np.stack(captured))
    from fit_band import fit
    best=fit(scene)
    scores=json.loads((OUT/'band-fit.json').read_text())
    apply_polish(best[0])
    set_flags(best[1])
    for lamp,watt,d in zip(lamps,best[2:],inputs):
        lamp.data.energy=watt;d['watts']=watt
        if watt<=0:
            bpy.data.objects.remove(lamp,do_unlink=True)
    cfg={'parent_sha256':PARENT,'pose':[-.313,-.045,10.3],'parent_gloss_contributions_mean_linear_crop':contribution,
        'polish_fraction_multiplier':best[0],'section_weights':weights.reshape(13,64)[:,0].tolist(),
        'lamps':[d for d in inputs if d['watts']>0],'mane_illumination_multiplier':best[1],
        'attenuated_mane_light_copies':[o.name for o in flags],
        'parent_fit_error':scores['parent']['loss'],'fitted_error':scores['predicted']['loss'],
        'packed_atlas_changed':False,'geometry_changed':False,'fit_display_crop':RECT}
    scene['knight_improvement_003_A']=json.dumps(cfg)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    scene.cycles.use_light_tree=True
    configure_render(scene,144);save_model(scene,OUT/'knight.blend')
    cfg['model_sha256']=sha(OUT/'knight.blend');json_file(OUT/'parameters.json',cfg)
    print('POLL_FINAL_FIT',best,cfg['parent_fit_error'],cfg['fitted_error'],flush=True)


def matched_studio():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'knight.blend'),load_ui=False);scene=bpy.context.scene
    info=json.loads((OUT/'parameters.json').read_text())
    for desc in info['lamps']:
        bpy.data.objects[desc['name']].hide_render=True
    for name in info['attenuated_mane_light_copies']:
        bpy.data.objects[name].hide_render=True
        bpy.data.objects[name.removeprefix('Poll flag | ')].light_linking.receiver_collection=None
    configure_render(scene,144);render(scene,OUT/'matched-parent-rig.png')
    use_side_camera(scene);render(scene,OUT/'matched-parent-rig-side.png')


if __name__=='__main__':
    build()
    pictures()
    matched_studio()
