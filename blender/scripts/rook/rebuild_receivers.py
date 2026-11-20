"""Regenerate exact-position render partitions from the current closed control."""
import bpy,numpy as np

def rebuild(scene, floor_receiver=None):
 body=next(o for o in scene.objects if o.get('rook_editable_control'))
 old=[o for o in scene.objects if o.get('rook_render_receiver')]
 if floor_receiver is None:floor_receiver=any(o.get('rook_render_receiver')=='floor_edge' for o in old)
 links={c.name:{o.get('rook_render_receiver') for o in c.objects if o in old} for c in bpy.data.collections}
 ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
 co=np.array([v.co[:] for v in m.vertices],np.float32);lv=np.array([l.vertex_index for l in m.loops]);starts=np.array([p.loop_start for p in m.polygons]);counts=np.array([p.loop_total for p in m.polygons]);centers=np.add.reduceat(co[lv],starts,axis=0)/counts[:,None];z=centers[:,2];r=np.linalg.norm(centers[:,:2],axis=1)
 labels=np.zeros(len(counts),int);labels[((z>2.68)&(r>.50))|((z>2.53)&(z<2.58)&(r>.58))]=1;labels[(z>.65)&(z<.74)&(r>.60)]=2;labels[(z>.18)&(z<.24)&(r>.84)]=3
 nz=np.array([p.normal.z for p in m.polygons]);labels[(labels==1)&(z>2.68)&(nz>.65)&(nz<.98)]=4
 if floor_receiver:
  floor_z=float(body.data.vertices[58*128].co.z);labels[(labels==0)&(z>floor_z-.001)&(z<floor_z+.06)&(r>.47)&(r<.56)&(nz>.6)&(nz<.99)]=5
 normals=np.array([n.vector[:] for n in m.corner_normals],np.float32);uvs={u.name:np.array([v.uv[:] for v in u.data],np.float32) for u in m.uv_layers};parts={}
 for ob in old:bpy.data.objects.remove(ob,do_unlink=True)
 for label,name in enumerate(['body','rim','shoulder','foot','rim_bevel']+(['floor_edge'] if floor_receiver else [])):
  ids=np.flatnonzero(labels==label);loops=np.concatenate([np.arange(starts[i],starts[i]+counts[i]) for i in ids]);verts,inv=np.unique(lv[loops],return_inverse=True);faces=[x.tolist() for x in np.split(inv,np.cumsum(counts[ids])[:-1])]
  me=bpy.data.meshes.new('Rook receiver '+name);me.from_pydata(co[verts].tolist(),[],faces);me.update()
  for i,p in enumerate(me.polygons):p.use_smooth=m.polygons[int(ids[i])].use_smooth
  for un,uv in uvs.items():me.uv_layers.new(name=un).data.foreach_set('uv',uv[loops].reshape(-1))
  me.normals_split_custom_set(normals[loops].tolist())
  for mat in body.data.materials:me.materials.append(mat)
  ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);ob.matrix_world=body.matrix_world.copy();ob['rook_render_receiver']=name;parts[name]=ob
 for collection,tags in links.items():
  for tag in tags:
   if parts[tag].name not in bpy.data.collections[collection].objects:bpy.data.collections[collection].objects.link(parts[tag])
 ev.to_mesh_clear();return parts
