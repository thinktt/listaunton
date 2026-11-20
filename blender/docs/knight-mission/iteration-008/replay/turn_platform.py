"""Turn a level platform on the existing pedestal without moving the carving."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

PARENT = '1a8c2b2384ac360766d3a3121671199f231df21b2ceea6caee22c9ebdb5e9766'
# The 64-point rings run from the floor to the top center. Exterior radii below
# the upper lip stay at the previous turning. Three coplanar rings retain a
# level surface through Catmull-Clark subdivision.
PROFILES = {
    'level': [(1.213,1.451),(1.226,1.474),(1.226,1.500),(1.211,1.521),
              (1.122,1.605),(1.138,1.695),(1.128,1.695),(1.096,1.695),(.001,1.695)],
    'cove': [(1.213,1.451),(1.226,1.474),(1.226,1.500),(1.211,1.521),
             (1.160,1.565),(1.116,1.635),(1.125,1.695),(1.112,1.695),(.001,1.695)],
    'shoulder': [(1.213,1.451),(1.226,1.474),(1.226,1.500),(1.211,1.521),
                 (1.174,1.565),(1.154,1.662),(1.148,1.710),(1.118,1.710),(.001,1.710)],
    'rolled': [(1.213,1.451),(1.226,1.474),(1.226,1.500),(1.211,1.521),
               (1.175,1.566),(1.157,1.649),(1.134,1.695),(1.099,1.695),(.001,1.695)],
    'high': [(1.213,1.451),(1.226,1.474),(1.226,1.520),(1.219,1.585),
             (1.212,1.673),(1.209,1.714),(1.194,1.730),(1.157,1.730),(.001,1.730)],
    'low': [(1.213,1.451),(1.226,1.474),(1.226,1.500),(1.225,1.541),
            (1.220,1.613),(1.213,1.645),(1.193,1.660),(1.162,1.660),(.001,1.660)],
}

def turn(obj, profile):
    xyz = np.empty((len(obj.data.vertices),3),np.float32)
    obj.data.vertices.foreach_get('co',xyz.ravel())
    rings=xyz.reshape(-1,64,3).copy()
    assert len(rings)==31 and obj.modifiers[0].type=='SUBSURF'
    assert np.ptp(rings[:,:,2],axis=1).max()<1.e-5
    radius=np.linalg.norm(rings[:,:,:2],axis=2).mean(1)
    for idx,(new_radius,height) in enumerate(profile,22):
        rings[idx,:,:2] *= new_radius/radius[idx]
        rings[idx,:,2]=height
    xyz_new=rings.reshape(-1,3)
    assert np.array_equal(xyz_new[:22*64],xyz[:22*64])
    obj.data.vertices.foreach_set('co',xyz_new.ravel());obj.data.update()
    bpy.context.view_layer.update()
    return {'control_rings':len(rings),'first_changed_ring':22,
            'max_vertex_shift':float(np.linalg.norm(xyz-xyz_new,axis=1).max()),
            'profile_r_z':profile}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('profile',choices=PROFILES)
    p.add_argument('out',type=Path);p.add_argument('--samples',type=int,default=36)
    p.add_argument('--source',type=Path);p.add_argument('--source-sha',default=PARENT)
    p.add_argument('--full',action='store_true')
    p.add_argument('--satin',action='store_true',help='Reduce varnish on the platform and upper shoulder')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    root=args.root.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/'scripts/knight'))
    from mission_scene import MODEL,ASSETS,json_file,sha,save_model,configure_render,render,use_side_camera,visible_meshes
    from export_mission import export
    source=args.source or MODEL
    assert sha(source)==args.source_sha
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
    info=turn(scene.objects['Knight | turned pedestal'], PROFILES[args.profile])
    if args.satin:
        obj=scene.objects['Knight | turned pedestal']
        attr=obj.data.attributes['Knight varnish coverage']
        value=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',value)
        factors=[1,1,1,.38,.10,.12,.21,.29,.30]
        value.reshape(31,64)[22:]*=np.array(factors)[:,None]
        attr.data.foreach_set('value',value);obj.data.update()
        info['upper_ring_polish_factors']=factors
    scene['knight_flat_platform']=json.dumps(info)
    configure_render(scene,144);save_model(scene,out/'knight.blend')
    bpy.ops.wm.open_mainfile(filepath=str(out/'knight.blend'),load_ui=False);scene=bpy.context.scene
    tex=ASSETS/json.loads((ASSETS/'mission-checkpoint.json').read_bytes())['texture_file']
    packed=visible_meshes(scene)[0].data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    assert bytes(packed.packed_file.data)==tex.read_bytes()
    meta=export(scene,tex,output=out,source=out/'knight.blend')
    configure_render(scene,args.samples)
    scene.render.resolution_percentage=100 if args.full else 66
    render(scene,out/'wood.png')
    use_side_camera(scene);render(scene,out/'wood-side.png')
    if args.full:
        for ob in visible_meshes(scene):ob.data.materials[0]=bpy.data.materials['Neutral satin clay']
        render(scene,out/'clay-side.png')
        bpy.ops.wm.open_mainfile(filepath=str(out/'knight.blend'),load_ui=False);scene=bpy.context.scene
        configure_render(scene,args.samples)
        for ob in visible_meshes(scene):ob.data.materials[0]=bpy.data.materials['Neutral satin clay']
        render(scene,out/'clay-fixed.png')
    json_file(out/'platform.json',{**info,'source':sha(source),'model':sha(out/'knight.blend'),
              'camera':meta['referenceCamera'],'atlas':sha(tex),'samples':args.samples,'full':args.full})
    print('PLATFORM_RENDERED',args.profile,sha(out/'knight.blend'))
if __name__=='__main__':main()
