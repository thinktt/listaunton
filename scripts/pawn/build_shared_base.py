"""Transfer the accepted queen turning to a single editable pawn lathe."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from mission_render import ROOT, control, fixed_camera, render, save_json, setup, sha
from polish_trial import open_source
sys.path.insert(0, str(HERE.parent / "king"))
from match_queen_base import SEGMENTS, coordinates, native_queen, side_faces

# Pair the same wood landmarks from the two turnings while retaining the pawn's
# cylindrical seam. A fractional row interpolates the existing UV, not the mesh.
DONOR_UV = [(0,0),(1,1),(2,1.45),(5,4.2),(6,6),(8,7.6),(11,9),(17,12),
            (21,15),(23,17),(25,19),(27,20.4),(29,22),(31,24),(33,26),
            (36,27),(38,28),(39,28.45)]
FIRST_UPPER = 29
WAIST = 31
COLLAR_BOTTOM = 34
BALL_SEAT = 42


def lathe_uv(old, new, rows):
    count = len(old.vertices) // SEGMENTS
    expected = side_faces(count)
    loops = np.empty(len(old.loops), dtype=np.int32)
    old.loops.foreach_get("vertex_index", loops)
    np.testing.assert_array_equal(loops[:-2*SEGMENTS], expected.ravel())
    for layer in old.uv_layers:
        values = np.empty((len(old.loops), 2), dtype=np.float32)
        layer.data.foreach_get("uv", values.ravel())
        faces = values[:-2*SEGMENTS].reshape(count-1,SEGMENTS,4,2)
        # Keep both horizontal edge corners for every longitude, including the UV seam.
        np.testing.assert_allclose(faces[:-1,:,[3,2]], faces[1:,:,[0,1]], atol=1e-6, rtol=0)
        edges = np.concatenate((faces[:,:,[0,1],:], faces[-1:,:,[3,2],:]),axis=0)
        low = np.floor(rows).astype(int)
        high = np.ceil(rows).astype(int)
        fraction = (rows-low)[:,None,None,None]
        uv = ((1-fraction)*edges[low]+fraction*edges[high]).astype(np.float32)
        bands = np.concatenate((uv[:-1], uv[1:,:,::-1]),axis=2)
        all_values = np.vstack((bands.reshape(-1,2), values[-2*SEGMENTS:]))
        dest = new.uv_layers.new(name=layer.name)
        dest.data.foreach_set("uv", all_values.ravel())
        np.testing.assert_array_equal(uv[40:], edges[FIRST_UPPER:])
    new.uv_layers.active = new.uv_layers[old.uv_layers.active.name]
    for layer in old.uv_layers:
        new.uv_layers[layer.name].active_render = layer.active_render


def hermite(t, start, end, start_slope, span):
    # The pawn stem has a level tangent at its waist.
    return (2*t**3-3*t**2+1)*start + (t**3-2*t**2+t)*span*start_slope + (-2*t**3+3*t**2)*end


def refit_upper(old, base, spec, total_height):
    upper = old[FIRST_UPPER:].copy()
    old_r = np.linalg.norm(old[:,0,:2],axis=1)
    old_z = old[:,0,2]
    floor = base[0,0,2]
    old_height = old_z[-1] - old_z[0]
    delta = total_height - old_height
    contact = old_z[BALL_SEAT] + delta * spec.get("stem_share", .78) + spec.get("seat_lift", 0)
    collar_bottom = old_z[COLLAR_BOTTOM] + (contact-old_z[BALL_SEAT]) + spec.get("collar_compression", 0)
    waist_z = old_z[WAIST] + .70*(collar_bottom-old_z[COLLAR_BOTTOM]) - spec.get("waist_lowering",0)
    # Use original relative heights within each feature, including the small
    # inward return where the ball sits inside the collar.
    z = old_z.copy()
    for a,b,dest_a,dest_b in [(28,WAIST,base[-1,0,2],waist_z),
            (WAIST,COLLAR_BOTTOM,waist_z,collar_bottom),
            (COLLAR_BOTTOM,BALL_SEAT,collar_bottom,contact),
            (BALL_SEAT,len(old)-1,contact,floor+total_height)]:
        t = (old_z[a:b+1]-old_z[a])/(old_z[b]-old_z[a])
        z[a:b+1]=dest_a+t*(dest_b-dest_a)
    head = slice(BALL_SEAT,None)
    t = (old_z[head]-old_z[BALL_SEAT])/(old_z[-1]-old_z[BALL_SEAT])
    seat_delta = contact-old_z[BALL_SEAT]
    top_delta = floor+total_height-old_z[-1]
    z[head] = old_z[head] + seat_delta + (top_delta-seat_delta)*t**spec.get("dome_falloff",1)
    radius = old_r.copy()
    stem_r = old_r[WAIST]*spec.get("waist_factor",1)
    collar_factor = spec.get("collar_factor",1)
    ball_factor = spec.get("ball_factor",1)
    radius[WAIST:] *= np.interp(np.arange(WAIST,len(old)),[WAIST,COLLAR_BOTTOM,40,BALL_SEAT,45],
                                [spec.get("waist_factor",1),collar_factor,collar_factor,ball_factor,ball_factor])
    last = np.linalg.norm(base[-1,0,:2])
    slope = (last-np.linalg.norm(base[-2,0,:2]))/(base[-1,0,2]-base[-2,0,2])
    span = waist_z - base[-1,0,2]
    assert span>.20 and last>stem_r
    t = (z[FIRST_UPPER:WAIST] - base[-1,0,2])/span
    radius[FIRST_UPPER:WAIST]=hermite(t,last,stem_r,slope,span)
    upper[:,:,:2] *= (radius[FIRST_UPPER:]/old_r[FIRST_UPPER:])[:,None,None]
    upper[:,:,2] = z[FIRST_UPPER:,None]
    return upper


def install(body, queen, spec, original, donor_foot):
    old = body.data
    assert old.shape_keys is None and not body.vertex_groups
    assert [l.name for l in old.uv_layers]==["Pawn pigment"]
    assert not any(a.data_type=="FLOAT" and not a.name.startswith(".") for a in old.attributes)
    old_coords = coordinates(body, SEGMENTS)
    width = original["diameter"]*spec["width_factor"]
    height = original["height"]*spec["height_factor"]
    scale = width/donor_foot
    base = queen.astype(np.float64)*scale
    base[:,:,2] += old_coords[0,0,2]-base[0,0,2]
    upper = refit_upper(old_coords,base,spec,height)
    xyz = np.concatenate((base,upper)).astype(np.float32)
    rows = np.r_[np.interp(np.arange(40),*np.asarray(DONOR_UV).T),np.arange(FIRST_UPPER,len(old_coords))]
    faces = side_faces(len(xyz)).tolist()
    faces += [list(reversed(range(SEGMENTS))),list(range((len(xyz)-1)*SEGMENTS,len(xyz)*SEGMENTS))]
    mesh = bpy.data.meshes.new("Pawn with shared Staunton turning")
    mesh.from_pydata(xyz.reshape(-1,3).tolist(), [], faces)
    mesh.update()
    mesh.polygons.foreach_set("use_smooth",np.ones(len(faces),bool))
    for mat in old.materials:
        mesh.materials.append(mat)
    lathe_uv(old,mesh,rows)
    body.data = mesh
    if not old.users:
        bpy.data.meshes.remove(old)
    base_error=float(np.abs(coordinates(body,SEGMENTS)[:40]-base).max())
    assert base_error<2e-7
    return {"uniform_scale":scale,"target_foot_diameter":width,"target_height":height,
            "floor":float(old_coords[0,0,2]),"donor_control_max_error":base_error,
            "base_rings":39,"stem_support_rings":1}


def measured(scene,body):
    bpy.context.view_layer.update()
    obj = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = obj.to_mesh()
    try:
        xyz=np.empty((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get("co",xyz.ravel())
    finally:
        obj.to_mesh_clear()
    section=xyz[(abs(xyz[:,1])<1e-6)&(xyz[:,0]>0)][:,[0,2]]
    return np.ptp(xyz,axis=0),section


def run(cfg,names):
    queen_path=ROOT/cfg["queen"]
    assert sha(queen_path)==cfg["queen_sha256"] and sha(ROOT/cfg["king"])==cfg["king_sha256"]
    with open(ROOT/cfg["starting_dimensions"],encoding="utf-8") as fp:
        dims=json.load(fp)
    assert dims["model_sha256"]==cfg["source_sha256"]
    queen,_=native_queen(queen_path)
    assert queen.shape==(40,SEGMENTS,3)
    for row in cfg["candidates"]:
        if names and row["name"] not in names:
            continue
        scene,body = open_source(cfg)
        out=ROOT/cfg["output"]/row["name"]
        out.mkdir(exist_ok=True,parents=True)
        report=install(body,queen,row,dims,cfg["donor_foot_diameter"])
        bounds,section=measured(scene,body)
        report.update(actual_diameter=float(bounds[0]),actual_height=float(bounds[2]),spec=row,
                      queen_sha256=cfg["queen_sha256"],source_sha256=cfg["source_sha256"])
        assert abs(bounds[0]-report["target_foot_diameter"])<.002
        assert abs(bounds[2]-report["target_height"])<.0005
        assert np.max(np.abs(np.asarray(body.matrix_world)-np.eye(4)))<1e-6
        np.save(out/"meridian.npy",section)
        scene["pawn_shared_base"]=json.dumps(report,sort_keys=True)
        scene["pawn_accepted_trial"]=row["name"]
        fixed_camera(scene)
        model=out/"pawn.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(model),compress=True)
        render(scene,out/"fixed.png")
        side=bpy.data.scenes[scene["pawn_side_scene"]]
        assert control(side) is body
        bpy.context.window.scene=side
        setup(side,cfg["samples"])
        side.render.resolution_x=side.render.resolution_y=cfg.get("side_resolution",800)
        render(side,out/"side.png")
        report.update(model_sha256=sha(model),fixed_sha256=sha(out/"fixed.png"),side_sha256=sha(out/"side.png"))
        save_json(out/"geometry.json",report)
        print("PAWN_SHARED_BASE_TRIAL",row["name"],bounds.tolist(),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("config",type=Path)
    parser.add_argument("candidates",nargs="*")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text(encoding="utf-8")),args.candidates)
