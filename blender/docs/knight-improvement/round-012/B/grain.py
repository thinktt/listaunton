"""Carry the actual flank wood through the cut in physical coordinates."""
import numpy as np
from mathutils.bvhtree import BVHTree

def ease(v):
    t=np.clip(v,0.,1.)
    return t*t*(3-2*t)

def reroute(obj,old,new,mid,back,front,edge,pull,amount,query=None):
    # Intersect the uncut maneuver's near or far flank at the new native
    # x/z. The pre-existing billet supplies its exact original colour and
    # its own patch of UV grain on the same physical side.
    me=obj.data;me.calc_loop_triangles();tri=np.empty((len(me.loop_triangles),3),np.int32)
    tl=np.empty_like(tri);me.loop_triangles.foreach_get('vertices',tri.ravel())
    me.loop_triangles.foreach_get('loops',tl.ravel());xyz=old[tri]
    tree=BVHTree.FromPolygons(old.tolist(),tri.tolist(),all_triangles=True)
    layer=me.uv_layers['Knight wood atlas']
    uv=np.empty((len(me.loops),2),np.float32);layer.data.foreach_get('uv',uv.ravel())
    lv=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',lv)
    x,y,z=old.T;nx=new[:,0]
    # UV scales remain those of the original wood. Fade toward the ridge
    # of the back and near the buried analytical closing cap.
    gate=ease((abs(y-mid)-.055)/.100)*ease((nx-back)/.115)
    lookup=x+gate*amount*(nx-x) if query is None else x+gate*(query-x)
    valid=(abs(lookup-x)>.00002)
    target=np.full((len(x),2),np.nan)
    for i in np.where(valid)[0]:
        sg=1 if y[i]>mid[i] else -1
        hit=tree.ray_cast((lookup[i],sg*2.5,z[i]),(0,-sg,0))
        j=hit[2]
        if j is None:continue
        ab=xyz[j,1]-xyz[j,0];ac=xyz[j,2]-xyz[j,0];p=np.asarray(hit[0])-xyz[j,0]
        a,b,c=ab@ab,ab@ac,ac@ac;det=a*c-b*b
        if det<1e-17:continue
        v=(c*(ab@p)-b*(ac@p))/det;w=(a*(ac@p)-b*(ab@p))/det
        target[i]=[1-v-w,v,w]@uv[tl[j]]
    diff=target[lv]-uv
    # Triangle islands are packed separately. Loops on a disjoint cap
    # keep their own island; they never interpolate through another piece.
    use=np.isfinite(diff).all(1)&(np.linalg.norm(diff,axis=1)<.16)
    uv[use]+=diff[use].astype(np.float32)
    layer.data.foreach_set('uv',uv.ravel())
    print('Native wood reflow',amount,int(use.sum()),'loop coordinates; furthest',np.linalg.norm(diff[use],axis=1).max(),flush=True)
