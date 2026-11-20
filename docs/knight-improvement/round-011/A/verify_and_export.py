"""Audit native geometry, region protection, inherited pigment and WebGL export."""
from pathlib import Path
import hashlib,json,sys
import bpy,bmesh,numpy as np
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from anatomy import chart
from mission_scene import visible_meshes,world_vertices,sha
from lower_carving_fit import rest_coords
from export_mission import export
def array_sha(v):return hashlib.sha256(v.tobytes()).hexdigest()
def observe(file):
    bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False);s=bpy.context.scene
    data={'sha256':sha(file),'pose':json.loads(s['knight_mission_pose']),'meshes':{},'lights':{}}
    p=data['pose'];pose=[p[k] for k in ('dx','dy','twist_degrees')];arrays={}
    for ob in visible_meshes(s):
        me=ob.data;v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel())
        wax=np.empty(len(v),np.float32);me.attributes['Knight varnish coverage'].data.foreach_get('value',wax)
        assert np.isfinite(wax).all() and wax.min()>=0 and wax.max()<=1
        arr=rest_coords(world_vertices(ob),pose);bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
        layers={}
        for uv in me.uv_layers:
            coords=np.empty((len(uv.uv),2),np.float32);uv.uv.foreach_get('vector',coords.ravel());assert np.isfinite(coords).all()
            layers[uv.name]={'sha256':array_sha(coords),'min':coords.min(0).tolist(),'max':coords.max(0).tolist()}
        idx=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',idx)
        data['meshes'][ob.name]={'verts':len(v),'faces':len(me.polygons),'uv':layers,
              'topology':array_sha(idx),'nonmanifold_edges':bad,'varnish_range':[float(wax.min()),float(wax.max())]}
        arrays[ob.name]=(v,wax,arr)
    for ob in s.objects:
        if ob.type=='LIGHT':data['lights'][ob.name]=[np.asarray(ob.matrix_world).tolist(),ob.data.shape,ob.data.size,ob.data.size_y,ob.data.energy,ob.data.spread,
              ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None,ob.hide_render]
    data['camera']=[np.asarray(s.camera.matrix_world).tolist(),s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
    data['packed']={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
    return data,arrays
def main():
    selected=D/'knight.blend';parent,v0=observe(D/'parent.blend');new,v1=observe(selected)
    assert new['packed']==parent['packed'] and new['pose']==parent['pose'] and new['camera']==parent['camera']
    assert set(new['meshes'])==set(parent['meshes'])
    changed=[k for k in new['lights'] if new['lights'][k]!=parent['lights'][k]]
    assert set(changed)=={'Eye reflection upper','Eye reflection lower'}
    protected={}
    for name,(v,w,r) in v0.items():
        m=new['meshes'][name];old=parent['meshes'][name];assert m['nonmanifold_edges']==0
        current,finish,_=v1[name]
        if name.endswith(' eye'):
            assert len(current)==7682 and len(v)==482 and set(m['uv'])==set(old['uv'])
            assert np.allclose(m['uv']['Knight wood atlas']['min'],old['uv']['Knight wood atlas']['min'])
            assert np.allclose(m['uv']['Knight wood atlas']['max'],old['uv']['Knight wood atlas']['max'])
            protected[name]={'natively_refined_uv_globe':[len(v),len(current)]}
        else:
            assert m['topology']==old['topology'] and m['uv']==old['uv']
            if 'head and neck' in name:
                u,t=chart(r);sel=np.hypot(u/.310,(t+.003)/.167)>=1.49
                assert np.array_equal(v[sel],current[sel]) and np.array_equal(w[sel],finish[sel])
                safe=(r[:,2]<3.6)|(r[:,2]>4.69)
                assert np.array_equal(v[safe],current[safe]) and np.array_equal(w[safe],finish[safe])
                protected[name]={'unchanged_outside_orbit':int(sel.sum()),'vertex_count':len(v),'unchanged_chest_and_crown':int(safe.sum())}
            else:
                assert np.array_equal(v,current) and np.array_equal(w,finish)
                protected[name]={'geometry_uv_and_varnish_all_exact':True}
    atlas=R/'assets/knight/wood-atlas-improvement-008-A.png';assert sha(atlas) in new['packed'].values()
    out=D/'webgl-check';out.mkdir(exist_ok=True)
    meta=export(bpy.context.scene,atlas,output=out,source=selected)
    assert meta['sourceSha256']==sha(selected) and meta['textureSha256']==sha(atlas) and meta['exactCornerData'] and len(meta['parts'])==7
    assert meta['finish']['file'] and (out/'varnish.bin').stat().st_size>0
    result={'parent':parent['sha256'],'model':new['sha256'],'atlas':sha(atlas),'protected':protected,'changed_lights':changed,
            'native':new['meshes'],'parent_meshes':parent['meshes'],'same_camera_and_pose':True,'packed_images_exact':True,
            'export_triangles':meta['triangleCount'],'export_parts':len(meta['parts']),'varnish_bytes':(out/'varnish.bin').stat().st_size}
    (D/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('VALIDATED',new['sha256'],meta['triangleCount'],flush=True)
if __name__=='__main__':main()
