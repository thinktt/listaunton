"""Verify exact scope of a collar turning experiment against its accepted source."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy, numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls,clear_light_path
from check_base_light_checkpoint import snapshot
from check_socket_checkpoint import extra
from focused_reflections import target

def positions():
    return {o.name:np.array([v.co[:] for v in o.data.vertices]) for o in controls(bpy.context.scene)}

def shadows():
    return {o.name:o.data.use_shadow for o in bpy.context.scene.objects if o.type=='LIGHT'}

def collar_crossings():
    body=next(o for o in controls(bpy.context.scene) if 'body' in o.name)
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
    bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices]);keep=(abs(co[:,1])<1e-7)&(co[:,0]>0)&(co[:,2]>2.7)&(co[:,2]<3.4)
    edges=[list(e.vertices) for e in mesh.edges if all(keep[i] for i in e.vertices)]
    segments=[co[p][:,[0,2]] for p in edges];crossings=[]
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    for i,(a,b) in enumerate(segments):
        d=b-a
        for j,(c,e) in enumerate(segments[i+1:],i+1):
            if set(edges[i])&set(edges[j]):continue
            v=e-c;den=cross(d,v)
            if abs(den)<1e-14:continue
            t=cross(c-a,v)/den;u=cross(c-a,d)/den
            if 1e-6<t<1-1e-6 and 1e-6<u<1-1e-6:crossings.append(dict(edges=[i,j],radius_z=(a+t*d).tolist()))
    ev.to_mesh_clear();return dict(section='positive X at y=0, z in (2.7,3.4)',segment_count=len(segments),crossings=crossings)

def main(before,after,config,output):
    cfg=json.loads((ROOT/config).read_text(encoding='utf-8-sig'))
    hashes=[hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (before,after)]
    a,old,_=snapshot(before);ae=extra();ac=positions();ash=shadows()
    b,new,receivers=snapshot(after);be=extra();bc=positions();bsh=shadows()
    for name,co in ac.items():
        expected=co.copy()
        if 'body' in name:
            expected=expected.reshape(-1,96,3)
            for key,(dr,dz) in cfg['profile_offsets'].items():
                row=expected[int(key)];r=np.linalg.norm(row[:,:2],axis=1)
                row[:,:2]*=((r+dr)/r)[:,None];row[:,2]+=dz
            expected=expected.reshape(-1,3).astype(np.float32).astype(float)
        assert np.array_equal(expected,bc[name]),('Unexpected control positions',name)
        b['objects'][name]['positions']=a['objects'][name]['positions']
    assert a==b,'Undeclared material, camera, UV, world or other control change'
    assert ae==be,'Float attributes or packed images changed'
    assert ash==bsh,'Shadow settings changed'
    sampling=bpy.context.scene.cycles
    assert sampling.samples==cfg.get('samples',128) and sampling.use_denoising
    if 'adaptive_sampling' in cfg:assert sampling.use_adaptive_sampling==cfg['adaptive_sampling']
    assert set(old)==set(new),'Lights added or deleted'
    allowed={row['name']:row for row in cfg.get('reaim',[])};probes=[]
    for name,state in old.items():
        expected=dict(state)
        if name in allowed:
            row=allowed[name];light=bpy.data.objects[name]
            hit,p,d,normal=target(bpy.context.scene,*row['pixel'])
            assert hit.get('king_render_region')==row['receiver']
            assert np.allclose(light.location[:],(p+d*row['distance'])[:],atol=1e-6,rtol=0)
            forward=(light.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
            assert forward.dot((p-light.location).normalized())>1-1e-6
            expected['matrix']=new[name]['matrix']
            for key in ('energy','size','size_y'):
                if key in row:expected[key]=float(np.float32(row[key]))
            probes.append(dict(name=name,point=list(p),normal=list(normal),clear_path=clear_light_path(bpy.context.scene,p,normal,d,row['distance'])))
        assert expected==new[name],('Undeclared light setting change',name)
    section=collar_crossings();assert not section['crossings']
    assert receivers['receiverCount']==9
    assert [hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (before,after)]==hashes
    report=dict(before=before,after=after,model_sha256=hashes[1],modified_profile_rows=sorted(map(int,cfg['profile_offsets'])),
        all_other_control_coordinates_exact=True,all_uvs_topology_float_attributes_material_images_exact=True,
        camera_world_color_management_light_paths_exact=True,all_other_light_settings_and_shadows_exact=True,
        edited_lights={name:new[name] for name in allowed},probes=probes,profile_section=section,render_receivers=receivers,
        render_sampling=dict(samples=sampling.samples,adaptive=sampling.use_adaptive_sampling,denoising=sampling.use_denoising))
    path=ROOT/output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('KING_COLLAR_TURNING_SCOPE_PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('config');p.add_argument('output')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.config,a.output)
