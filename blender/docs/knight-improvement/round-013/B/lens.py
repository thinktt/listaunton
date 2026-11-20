"""Rebuild the closed wooden eye as two ordered height surfaces on the native flank."""
import bpy,numpy as np
from mathutils.bvhtree import BVHTree

def rebuild(s,obj,fields,design):
    from carve import AX,UP,CENTER,chart,pose,rest_coords,posed,world_vertices,sample,ease,bell,relax_axis
    sg=-1 if obj.name.endswith('near eye') else 1;si=0 if sg<0 else 1
    p=pose(s);me=obj.data;orig=rest_coords(world_vertices(obj),p)
    me.calc_loop_triangles()
    tri=np.empty((len(me.loop_triangles),3),np.int32);loops=np.empty_like(tri)
    me.loop_triangles.foreach_get('vertices',tri.ravel());me.loop_triangles.foreach_get('loops',loops.ravel())
    tree=BVHTree.FromPolygons(orig.tolist(),tri.tolist(),all_triangles=True)
    # A monotone polar chart gives the outer and inner layers identical
    # projected triangulation and a positive physical gap at every vertex.
    na,nr=160,44
    th=np.arange(na)*2*np.pi/na;rr=np.repeat(np.arange(1,nr+1)/nr,na);tt=np.tile(th,nr)
    r=np.r_[0,rr];u=.020+np.r_[0,.314*rr*np.cos(tt)]
    center=.019-.055*u+.018*bell(u+.115,.086)
    v=center+np.r_[0,rr*(.119+.025*bell(u[1:]+.105,.142))*np.sin(tt)]
    xz=CENTER+u[:,None]*AX+v[:,None]*UP
    plane=sample(fields[si][4],u,v)
    # Both rim and back reside in the skull under the visible opening.
    front=plane-.063*ease((r-.775)/.215)
    thickness=.119-.084*ease((r-.43)/.57)
    count=len(u)
    pv=np.empty((2*count,3),float)
    nu,nv=relax_axis(u,v,design);newxz=CENTER+nu[:,None]*AX+nv[:,None]*UP
    pv[:count,0]=newxz[:,0];pv[:count,2]=newxz[:,1];pv[:count,1]=sg*front
    pv[count:]=pv[:count];pv[count:,1]-=sg*thickness
    world=posed(pv,*p);m=np.asarray(obj.matrix_world)
    local=(world-m[:3,3])@np.linalg.inv(m[:3,:3]).T
    face=[]
    at=lambda ring,j:1+(ring-1)*na+j%na
    for j in range(na):face.append((0,at(1,j),at(1,j+1)))
    for ring in range(1,nr):
        for j in range(na):face.append((at(ring,j),at(ring+1,j),at(ring+1,j+1),at(ring,j+1)))
    face+= [tuple(v+count for v in reversed(f)) for f in face]
    for j in range(na):face.append((at(nr,j+1),at(nr,j),at(nr,j)+count,at(nr,j+1)+count))
    if sg>0:face=[f[::-1] for f in face]
    output=bpy.data.meshes.new('Ordered wooden lens · '+('near' if sg<0 else 'far'))
    output.from_pydata(local.tolist(),[],face);output.update()
    # Retrieve point finish and all UV layers from the inherited billet
    # on this same physical flank; the buried back shares the front grain.
    ids=[];weights=[]
    for xx,zz,yy in zip(xz[:,0],xz[:,1],front):
        hit=tree.ray_cast((xx,2.*sg,zz),(0,-sg,0))
        if hit[2] is None:hit=tree.find_nearest((xx,yy*sg,zz))
        pos=np.asarray(hit[0]);t=hit[2];a,b,c=orig[tri[t]]
        ab,ac=b-a,c-a;d=pos-a;aa=ab@ab;bb=ac@ac;cc=ab@ac;det=aa*bb-cc*cc
        if det>1e-18:
            w1=(bb*(d@ab)-cc*(d@ac))/det;w2=(aa*(d@ac)-cc*(d@ab))/det;w=np.clip([1-w1-w2,w1,w2],0,1)
            w/=w.sum()
        else:w=[1,0,0]
        ids.append(t);weights.append(w)
    ids=np.array(ids);weights=np.array(weights)
    lv=np.empty(len(output.loops),np.int32);output.loops.foreach_get('vertex_index',lv);lv%=count
    for uv in me.uv_layers:
        a=np.empty((len(uv.data),2),np.float32);uv.data.foreach_get('uv',a.ravel())
        val=(weights[:,:,None]*a[loops[ids]]).sum(1)
        dest=output.uv_layers.new(name=uv.name);dest.data.foreach_set('uv',val[lv].astype(np.float32).ravel())
    for attr in me.attributes:
        if attr.name.startswith('.') or attr.domain!='POINT' or attr.data_type!='FLOAT':continue
        a=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',a)
        values=(weights*a[tri[ids]]).sum(1)
        if len(design)>11 and attr.name=='Knight varnish coverage':
            # Satin finish around the lower insertion, without a second glazed border.
            matte=ease((.022-v)/.078)*(.36+.34*ease((u-.02)/.19))
            values=values*(1-matte)+.08*matte
        dest=output.attributes.new(attr.name,'FLOAT','POINT');dest.data.foreach_set('value',np.tile(values,2).astype(np.float32))
    for mat in me.materials:output.materials.append(mat)
    for poly in output.polygons:poly.use_smooth=True
    obj.data=output
    return {'closed_mesh_vertices':2*count,'min_back_thickness':float(thickness.min()),'max_back_thickness':float(thickness.max())}
