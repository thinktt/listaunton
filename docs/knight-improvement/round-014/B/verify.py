"""Verify native shape, UVs, material, studio and actual delivery export."""
from pathlib import Path
import hashlib,json,runpy,shutil,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from candidate import load,MANE,sha
from map import unpose
from qa_geometry import inspect
import export_mission

def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()
def collect(s):
    geo={};uv={};top={};finish={};lights={};mane_uv=None;g=bpy.context.evaluated_depsgraph_get()
    for o in s.objects:
        if o.type=='LIGHT':
            l=o.data;coll=o.light_linking.receiver_collection
            lights[o.name]=[list(np.asarray(o.matrix_world).ravel()),l.energy,list(l.color),
                             l.shape,l.size,l.size_y,l.spread,sorted(x.name for x in coll.objects) if coll else None]
        if o.type!='MESH':continue
        ob=o.evaluated_get(g);me=ob.to_mesh();m=np.asarray(ob.matrix_world)
        n=o.name.removeprefix('Knight | ')
        c=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',c.ravel())
        geo[n]=unpose(s,c@m[:3,:3].T+m[:3,3])
        lv=np.empty(len(me.loops),np.int32);ls=np.empty(len(me.polygons),np.int32)
        me.loops.foreach_get('vertex_index',lv);me.polygons.foreach_get('loop_start',ls);top[n]=digest(np.concatenate([lv,ls]))
        uv[n]={}
        for layer in me.uv_layers:
            a=np.empty((len(me.loops),2),np.float32);layer.data.foreach_get('uv',a.ravel());uv[n][layer.name]=digest(a)
        attr=me.attributes.get('Knight varnish coverage')
        if attr:
            v=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',v);finish[n]=digest(v)
        ob.to_mesh_clear()
    cam=s.camera;C=[list(np.array(cam.matrix_world).ravel()),cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y,
                    s.render.resolution_percentage,s.render.resolution_x,s.render.resolution_y]
    node=s.objects['Knight | '+MANE].active_material.node_tree.nodes['Knight delivered albedo']
    pix=bytes(node.image.packed_file.data)
    return {'g':geo,'uv':uv,'mane_uv':mane_uv,'t':top,'f':finish,'lights':lights,'camera':C,
            'images':{i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file},
            'pigment':hashlib.sha256(pix).hexdigest(),'image':node.image.name,'path':node.image.filepath}

def main():
    a=collect(load('parent.blend'));s=load('knight.blend');b=collect(s)
    assert a['camera']==b['camera'] and a['lights']==b['lights'] and a['f']==b['f']
    assert a['t']==b['t'] and a['uv']==b['uv']
    diff={}
    for n in a['g']:
        ap=a['g'][n];bp=b['g'][n];delta=np.linalg.norm(ap-bp,axis=1)
        diff[n]=float(delta.max())
        assert diff[n]==0,n
    assert a['pigment']==sha(D/'parent-pigment.png') and b['pigment']==sha(D/'pigment.png')
    assert b['pigment']==s['knight_atlas_sha256']
    assert {k:v for k,v in a['images'].items() if k!=a['image']}=={k:v for k,v in b['images'].items() if k!=b['image']}
    crosses=inspect(s)
    assert all(p['folds']==0 for p in crosses.values())
    root=D/'review-copy';mdl=root/'models/knight';assets=root/'assets/knight'
    mdl.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    src=mdl/'knight-rebuilt.blend';shutil.copyfile(D/'knight.blend',src)
    tex=assets/Path(b['path']).name;shutil.copyfile(D/'pigment.png',tex)
    export_mission.ROOT=root;export_mission.export(s,tex,output=assets,source=src)
    sys.argv=['validate.py','--',str(root)];runpy.run_path(str(R/'scripts/knight/validate.py'),run_name='__main__')
    check=json.loads((assets/'validation.json').read_text())
    def h(x):
        q=np.concatenate([v[:,2] for n,v in x['g'].items() if n not in ['coherent skull cheek and conical muzzle','curved neck and chest']])
        return float(q.max()-q.min())
    (D/'verified.json').write_text(json.dumps({'model_sha256':sha(src),'parent_sha256':sha(D/'parent.blend'),
      'all_evaluated_uv_layers_identical':True,'all_evaluated_topology_identical':True,'max_displacement_by_mesh':diff,
      'all_lights_and_linking_identical':True,
      'camera_identical':True,'all_varnish_values_identical':True,'height_parent_candidate':[h(a),h(b)],
      'pigment':{'source':a['pigment'],'delivered':b['pigment'],'release_filename':tex.name},
      'intersections':crosses,'viewer_validation':check},indent=2)+'\n')
if __name__=='__main__':main()
