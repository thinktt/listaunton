"""Check the protected native surfaces, UVs, cameras, pigment, studio and poll."""
from pathlib import Path
import hashlib,json,sys
import bpy,bmesh,numpy as np
D=Path(__file__).resolve().parent;sys.path[:0]=[str(D),str(D.parents[2]/'scripts/knight')]
from mission_scene import sha,visible_meshes,world_vertices
from lower_carving_fit import rest_coords
from sections import rest_tree
def hash_array(x):return hashlib.sha256(x.tobytes()).hexdigest()
def sample(scene,file):
    cfg=json.loads(scene['knight_mission_pose']);pose=[cfg[k] for k in ('dx','dy','twist_degrees')]
    native={};values={}
    for obj in visible_meshes(scene):
        mesh=obj.data;pos=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get('co',pos.ravel())
        cov=np.empty(len(pos),np.float32);mesh.attributes['Knight varnish coverage'].data.foreach_get('value',cov)
        charts={}
        for layer in mesh.uv_layers:
            uv=np.empty((len(layer.uv),2),np.float32);layer.uv.foreach_get('vector',uv.ravel());charts[layer.name]=hash_array(uv)
        bm=bmesh.new();bm.from_mesh(mesh);non=sum(not k.is_manifold for k in bm.edges);bm.free()
        idx=np.empty(len(mesh.loops),np.int32);mesh.loops.foreach_get('vertex_index',idx)
        native[obj.name]={'verts':len(pos),'quads_and_faces':len(mesh.polygons),'topology':hash_array(idx),'uv':charts,'nonmanifold_edges':non}
        values[obj.name]=(pos,cov,rest_coords(world_vertices(obj),pose))
    lights={ob.name:[list(ob.matrix_world),ob.data.energy,ob.data.shape,ob.data.size,ob.data.size_y,ob.data.spread,
        ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None,ob.hide_render] for ob in scene.objects if ob.type=='LIGHT'}
    for v in lights.values():v[0]=[list(row) for row in v[0]]
    camera=[np.array(scene.camera.matrix_world).tolist(),scene.camera.data.ortho_scale,scene.camera.data.shift_x,scene.camera.data.shift_y]
    report={'sha':sha(file),'lights':lights,'camera':camera,'native':native,
            'packed':{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}}
    tree=rest_tree(scene,pose,'swept rounded mane');report['crown']={}
    for x in (-.8,-.6,-.4,-.2,0,.14):
        xp=np.arange(-.34,.3405,.001);z=[]
        for y in xp:
            hit=tree.ray_cast((x,y,5.8),(0,0,-1),1.13)[0];z.append(hit.z if hit else np.nan)
        z=np.array(z);inside=np.isfinite(z);z=z[inside];yp=xp[inside]
        peak=float(z.max());top=yp[z>=peak-.004]
        angles=np.degrees(np.arctan(abs(np.gradient(z,yp))))
        def width(sign):
            yy=yp*sign;order=np.argsort(yy);yy,aa=yy[order],angles[order];mask=(yy>.1)&(yy<.285)
            yy,aa=yy[mask],aa[mask]
            # First outward tangent crossings identify the shoulder in the
            # curved dome, well inside the separate lower edge of the flank.
            def crossing(deg):
                ids=np.flatnonzero(aa>=deg)
                if not len(ids):return np.nan
                i=ids[0]
                return yy[0] if i==0 else yy[i-1]+(deg-aa[i-1])/(aa[i]-aa[i-1])*(yy[i]-yy[i-1])
            return float(crossing(60)-crossing(30))
        report['crown'][str(x)]={'peak_z':peak,'upper_center_y':float((top.max()+top.min())*.5),'top_width_004':float(np.ptp(top)),
                         'near_lateral_run_30_to_60_degrees':width(-1),'far_lateral_run_30_to_60_degrees':width(1)}
    return report,values
def main():
    reports={};datas={}
    for tag,base in [('parent','parent'),('A','knight')]:
        f=D/(base+'.blend');bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False)
        reports[tag],datas[tag]=sample(bpy.context.scene,f)
    old,new=reports['parent'],reports['A']
    asserts={k:old[k]==new[k] for k in ('lights','camera','packed','native')}
    assert all(asserts.values()) and not any(k['nonmanifold_edges'] for k in new['native'].values())
    assert '86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978' in new['packed'].values()
    dif={}
    for name,(v,finish,q) in datas['parent'].items():
        w,new_finish,_=datas['A'][name];diff=np.linalg.norm(w-v,axis=1)
        item={'max_local_vertex_offset':float(diff.max()),'max_varnish_change':float(abs(new_finish-finish).max())}
        if 'swept ear' in name:
            assert np.array_equal(v[:128],w[:128])
            item['two_free_cage_rings_geometry_exact']=True
        elif 'mane' in name:
            assert np.array_equal(v.reshape(13,64,3)[7:],w.reshape(13,64,3)[7:])
            item['six_lower_rings_geometry_exact']=True
        elif 'head and neck' in name:
            safe=q[:,2]<=4.70
            assert np.array_equal(v[safe],w[safe]) and np.array_equal(finish[safe],new_finish[safe])
            item['eye_cheek_chest_region']={'exact_geometry_and_varnish':True,'tested_vertices':int(safe.sum()),'z_max':4.70}
        else:
            assert np.array_equal(v,w) and np.array_equal(finish,new_finish)
            item['geometry_and_varnish_exact']=True
        dif[name]=item
    report={'parent':old['sha'],'candidate':new['sha'],'studio_uv_and_topology_identity':asserts,'packed':new['packed'],'protected_parts':dif,
            'crown':{k:v['crown'] for k,v in reports.items()},'method':'Crown sampled with downward rest-space rays at 0.001-unit lateral intervals. Shoulder run is the lateral distance between the first 30 and 60 degree inclinations, taken outwards from either side of the central dome.'}
    (D/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VALIDATED',new['sha'],report['crown']['A']['-0.6'])
if __name__=='__main__':main()
