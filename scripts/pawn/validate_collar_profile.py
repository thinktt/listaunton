"""Validate a two-ring collar underside edit and one existing reflector.

The saved file must preserve every other control point, UV, shader, texture,
lamp, camera and sampling setting. The evaluated surface must remain closed.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Euler
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,sha,save_json
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from validate_local_surface import surface,sampling
from validate_groove_reflector import ramps
from mix_varnish import validate as band

def controls(body):
    mesh=body.data;co=np.array([v.co[:] for v in mesh.vertices],dtype=np.float32).reshape(-1,96,3)
    raw={}
    for label,seq,prop,width,dtype in [('loops',mesh.loops,'vertex_index',1,np.int32),
        ('faces',mesh.polygons,'loop_total',1,np.int32),('uv',mesh.uv_layers['Pawn pigment'].data,'uv',2,np.float32)]:
        a=np.empty(len(seq)*width,dtype);seq.foreach_get(prop,a);raw[label]=hashlib.sha256(a.tobytes()).hexdigest()
    raw['matrix']=[list(row) for row in body.matrix_world]
    raw['smooth']=[p.use_smooth for p in mesh.polygons]
    raw['modifiers']=[{key:getattr(m,key) for key in ('type','show_render','show_viewport','levels','render_levels','subdivision_type','uv_smooth','boundary_smooth') if hasattr(m,key)} for m in body.modifiers]
    return co,raw

def run(cfg,target,out):
    source=ROOT/cfg['source'];assert sha(source)==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene)
    before,control_state=controls(body);old=fingerprint(scene,body)
    old_graph=graph(surface(body),());old_ramps=ramps(body);old_band=band(scene,body);old_sampling=sampling(scene)
    finish=sha(ROOT/'assets/pawn/pawn-varnish-v9.png')
    assert hashlib.sha256(body.data.materials[0].node_tree.nodes['Pawn varnish roughness'].image.packed_file.data).hexdigest()==finish
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);after,new_controls=controls(body);new=fingerprint(scene,body)
    assert control_state==new_controls,'Control topology, UVs, smoothing, transform or modifiers changed'
    keys=sorted(map(int,cfg['profiles']));assert keys==[35,36]
    unaffected=[i for i in range(len(before)) if i not in keys]
    assert np.array_equal(before[unaffected],after[unaffected]),'Unlisted meridian control changed'
    assert np.allclose(before[:,:,:2],after[:,:,:2],atol=1e-7,rtol=0),'Radius changed'
    guide=json.loads((ROOT/'scripts/pawn/profile.json').read_text());align=json.loads((ROOT/'assets/pawn/original-alignment.json').read_text())
    scale=1254/(300*align['scale']*guide['scale']);edits={}
    for i in keys:
        radius,axis=cfg['profiles'][str(i)];z=(guide['y0']-axis)*scale/math.cos(math.radians(54))
        assert np.allclose(after[i,:,2],z,atol=1e-7,rtol=0)
        assert np.allclose(np.linalg.norm(after[i,:,:2],axis=1),radius*scale,atol=1e-7,rtol=0)
        assert -.09<float(after[i,0,2]-before[i,0,2])<0
        edits[str(i)]={'radius':float(np.linalg.norm(after[i,0,:2])),'z_before':float(before[i,0,2]),'z_after':float(after[i,0,2])}
    for key in ('world','ray_depth','prior_finish_inputs','other_packed_images'):assert old[key]==new[key],key
    assert graph(surface(body),())==old_graph and ramps(body)==old_ramps and band(scene,body)==old_band
    assert hashlib.sha256(body.data.materials[0].node_tree.nodes['Pawn varnish roughness'].image.packed_file.data).hexdigest()==finish
    assert sampling(scene)==old_sampling and old_sampling['samples']==cfg['samples']==512
    assert not scene.render.use_border and scene.render.resolution_percentage==100
    assert set(old['lights'])==set(new['lights'])
    permitted=cfg.get('fitted_lights',[]);assert len(permitted)<=1
    names={row['name'] for row in permitted};assert names<={'Lower collar glint'}
    for name in old['lights']:
        if name not in names:assert old['lights'][name]==new['lights'][name],name
    for row in permitted:
        ob=scene.objects[row['name']];d=ob.data
        assert d.type=='AREA' and d.shape=='ELLIPSE' and not ob.visible_diffuse and ob.visible_glossy
        assert np.allclose(ob.location,row['position'],atol=1e-7,rtol=0)
        assert np.allclose(ob.matrix_world.to_3x3(),Euler(row['rotation']).to_matrix(),atol=1e-7,rtol=0)
        for key,want in [('energy',row['energy']),('size',row['size']),('size_y',row['size_y']),('spread',math.radians(row['spread']))]:
            assert math.isclose(getattr(d,key),want,rel_tol=1e-6,abs_tol=1e-8),key
        assert np.allclose(d.color,row['color'],atol=1e-7,rtol=0)
        a,b=old['lights'][row['name']],new['lights'][row['name']]
        for key in ('diffuse','glossy','type','visibility'):assert a[key]==b[key],key
        for key in a['settings']:
            if key not in ('shape','size','size_y','spread'):assert a['settings'][key]==b['settings'][key],key
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
    volume=bm.calc_volume(signed=True);euler=len(bm.verts)-len(bm.edges)+len(bm.faces)
    assert all(e.is_manifold for e in bm.edges) and volume>0 and euler==2
    bm.free();ev.to_mesh_clear()
    report={'passed':True,'source_sha256':sha(source),'model_sha256':sha(target),'profile_edits':edits,
        'all_other_control_vertices_exact':True,'radii_preserved':True,'control_topology_uv_smoothing_modifiers_preserved':True,
        'full_shader_and_all_map_pixels_preserved':True,'all_ramps_preserved':True,'matte_band':old_band,
        'unchanged_lights':len(old['lights'])-len(names),'edited_lights':{n:new['lights'][n] for n in names},
        'world_and_ray_depth_preserved':True,'sampling':old_sampling,'camera_above_board':54,
        'closed_manifold':True,'euler':euler,'volume':volume,'evaluated_mesh_normals_uv_sha256':new['evaluated_mesh_normals_uv_sha256']}
    save_json(out,report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')),ROOT/a.model,ROOT/a.output)
