"""Export the visible evaluated carving, smooth corner normals and pigment UVs."""
from pathlib import Path
import sys
import math

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import ASSETS,ROOT,MODEL,json_file,sha,visible_meshes

LAYER = "Knight wood atlas"


def export(scene, texture, *, output=ASSETS, source=MODEL):
    graph=bpy.context.evaluated_depsgraph_get()
    vertex_blocks=[];index_blocks=[];parts=[];finish_blocks=[];satin_blocks=[]
    meshes=visible_meshes(scene)
    satin_name="Rubbed chest flats"
    has_satin=any(obj.data.attributes.get(satin_name) is not None for obj in meshes)
    vert_offset=index_offset=0
    for obj in meshes:
        ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
        co=np.empty((len(mesh.vertices),3),np.float32)
        normal=np.empty((len(mesh.loops),3),np.float32)
        uv=np.empty((len(mesh.loops),2),np.float32)
        loop_verts=np.empty(len(mesh.loops),np.int32)
        triangles=np.empty((len(mesh.loop_triangles),3),np.int32)
        mesh.vertices.foreach_get("co",co.ravel())
        mesh.corner_normals.foreach_get("vector",normal.ravel())
        mesh.loops.foreach_get("vertex_index",loop_verts)
        mesh.uv_layers[LAYER].data.foreach_get("uv",uv.ravel())
        mesh.loop_triangles.foreach_get("loops",triangles.ravel())
        transform=np.asarray(obj.matrix_world)
        co=co@transform[:3,:3].T+transform[:3,3]
        normal=normal@np.linalg.inv(transform[:3,:3])
        normal/=np.linalg.norm(normal,axis=1)[:,None]
        data=np.column_stack((co[loop_verts],normal,uv)).astype("<f4")
        varnish=mesh.attributes.get("Knight varnish coverage")
        if varnish is not None:
            coverage=np.empty(len(mesh.vertices),np.float32)
            varnish.data.foreach_get("value",coverage)
            assert np.isfinite(coverage).all() and coverage.min()>=0 and coverage.max()<=1
            keys=np.column_stack((data,np.rint(255*coverage[loop_verts])))
        else:
            keys=data
        if has_satin:
            assert varnish is not None
            attr=mesh.attributes.get(satin_name)
            satin=np.zeros(len(mesh.vertices),np.float32)
            if attr is not None:
                assert attr.domain=="POINT" and attr.data_type=="FLOAT"
                attr.data.foreach_get("value",satin)
                assert np.isfinite(satin).all() and satin.min()>=0 and satin.max()<=1
            keys=np.column_stack((keys,np.rint(255*satin[loop_verts])))
        unique,remap=np.unique(keys,axis=0,return_inverse=True)
        indices=remap.reshape(-1)[triangles].astype("<u4").ravel()
        assert np.array_equal(unique[indices],keys[triangles.ravel()])
        if has_satin:
            satin_blocks.append(unique[:,9].astype(np.uint8))
        if varnish is not None:
            finish_blocks.append(unique[:,8].astype(np.uint8))
            unique=unique[:,:8].copy()
        vertex_blocks.append(unique);index_blocks.append(indices+vert_offset)
        parts.append({"name":obj.name,"vertexCount":len(unique),"indexCount":len(indices),
            "indexOffset":index_offset,"vertexOffset":vert_offset,"triangleCount":len(indices)//3})
        vert_offset+=len(unique);index_offset+=len(indices)
        ev.to_mesh_clear()
    vertices=np.concatenate(vertex_blocks);indices=np.concatenate(index_blocks)
    raw=vertices.tobytes()+indices.astype("<u4").tobytes()
    (output/"mesh.bin").write_bytes(raw)
    lo=vertices[:,:3].min(0);hi=vertices[:,:3].max(0)
    cam=scene.camera
    projection=cam.calc_matrix_camera(graph,x=scene.render.resolution_x,y=scene.render.resolution_y)
    direction=np.asarray(cam.matrix_world)[:3,2]
    elevation=math.degrees(math.atan2(direction[2],np.linalg.norm(direction[:2])))
    assert abs(elevation-54)<1e-4 and cam.data.type=="ORTHO"
    camera={"type":"ORTHO","elevationDegrees":54,"yawDegrees":math.degrees(math.atan2(direction[0],-direction[1])),
            "worldToCamera":np.asarray(cam.matrix_world.inverted()).ravel().tolist(),
            "projectionMatrix":np.asarray(projection).ravel().tolist(),"width":scene.render.resolution_x,
            "height":scene.render.resolution_y,"orthoScale":cam.data.ortho_scale,
            "shiftX":cam.data.shift_x,"shiftY":cam.data.shift_y}
    meta={"vertexCount":len(vertices),"indexCount":len(indices),"triangleCount":len(indices)//3,
          "vertexStrideBytes":32,"vertexByteLength":vertices.nbytes,"indexByteOffset":vertices.nbytes,
          "totalByteLength":len(raw),"bounds":{"min":lo.tolist(),"max":hi.tolist(),"size":(hi-lo).tolist(),"center":((hi+lo)/2).tolist()},
          "parts":parts,"sourceSha256":sha(source),"referenceCamera":camera,"texture":texture.relative_to(ROOT).as_posix(),
          "textureSha256":sha(texture),"uvLayer":LAYER,"exactCornerData":True}
    if finish_blocks:
        assert len(finish_blocks)==len(parts)
        finish=output/"varnish.bin"
        finish.write_bytes(np.concatenate(finish_blocks).tobytes())
        assert finish.stat().st_size==len(vertices)
        relief=visible_meshes(scene)[0].data.materials[0].node_tree.nodes.get("Open walnut grain under the varnish")
        meta["finish"]={"file":finish.relative_to(ROOT).as_posix(),"sha256":sha(finish),
                        "attribute":"Knight varnish coverage","encoding":"unorm8",
                        "reliefDistance":relief.inputs["Distance"].default_value if relief else 0}
    if has_satin:
        data=output/"satin.bin"
        data.write_bytes(np.concatenate(satin_blocks).tobytes())
        assert data.stat().st_size==len(vertices)
        surface=meshes[0].data.materials[0].node_tree.nodes["Satin walnut in open grain"]
        parameters={}
        for name in ("Roughness","Specular IOR Level","Coat Weight"):
            adjustment=surface.inputs[name].links[0].from_node
            assert adjustment.operation=="MULTIPLY_ADD"
            assert adjustment.inputs[0].links[0].from_node.attribute_name==satin_name
            parameters[name]=[adjustment.inputs[i].default_value for i in (2,1)]
        meta["satin"]={"file":data.relative_to(ROOT).as_posix(),"sha256":sha(data),
                       "attribute":satin_name,"encoding":"unorm8","parameters":parameters}
    json_file(output/"camera.json",camera);json_file(output/"mesh.json",meta)
    return meta
