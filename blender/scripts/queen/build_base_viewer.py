"""Build the base study's exact, shared-pose orbit viewer and register its reference images."""
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from viewer_document import make_document

PUBLIC = ROOT/"assets/queen-base-studies"
MODELS = ROOT/"models/queen-base-studies"
BUILD = ROOT/"build/queen-base-studies"
IDS = ("socket","compressed")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exact_patch(before, after):
    """Store runs of changed 32-bit words, including any changed triangle indices."""
    if len(before) != len(after) or len(before)%4:
        raise ValueError("The mesh exports must share a buffer layout")
    a, b = np.frombuffer(before,"<u4"), np.frombuffer(after,"<u4")
    changes = np.flatnonzero(a!=b)
    if not len(changes):
        raise ValueError("The base variant has identical geometry")
    cuts = np.flatnonzero(np.diff(changes)>4)+1
    runs = list(zip(changes[np.r_[0,cuts]], changes[np.r_[cuts-1,len(changes)-1]]+1))
    patch = bytearray(struct.pack("<4sII",b"QBP1",len(before),len(runs)))
    restored = bytearray(before)
    for lo,hi in runs:
        start,end = 4*int(lo),4*int(hi)
        patch.extend(struct.pack("<II",start,end-start))
        patch.extend(after[start:end])
        restored[start:end] = after[start:end]
    if restored != after:
        raise ValueError("Mesh patch did not reproduce the evaluated Blender export")
    return patch


def main():
    cfg = json.loads(Path(__file__).with_name("base-study-profile.json").read_text())
    baseline = (BUILD/"socket/mesh.bin").read_bytes()
    meta = json.loads((BUILD/"socket/mesh.json").read_text())
    assert cfg["source_sha256"] == meta["sourceSha256"] == sha((MODELS/"socket.blend").read_bytes())
    material = meta["materialConfig"]
    public, evidence, tags = {}, {}, []
    for key in IDS:
        info = json.loads((BUILD/key/"mesh.json").read_text())
        data = (BUILD/key/"mesh.bin").read_bytes()
        assert sha((MODELS/(key+".blend")).read_bytes()) == info["sourceSha256"]
        assert info["validation"]["binaryRoundTripExact"] and not info["validation"]["simplificationApplied"]
        assert info["referenceCamera"] == meta["referenceCamera"]
        for bound in ("min","max","size","center"):
            assert np.allclose(info["bounds"][bound], meta["bounds"][bound], atol=2e-6, rtol=0), (key,bound)
        for field in ("vertexCount","vertexStrideBytes","indexCount","vertexByteLength","indexByteOffset","totalByteLength","uvOffsetBytes"):
            assert info[field] == meta[field],(key,field)
        for field in ("texture_sha256","value","saturation","image_mix"):
            assert info["materialConfig"][field] == material[field]
        public[key] = {"sourceSha256":info["sourceSha256"],"download":"../../models/queen-base-studies/"+key+".blend"}
        evidence[key] = {"model_sha256": info["sourceSha256"], "mesh_sha256": sha(data), "triangles": info["triangleCount"]}
        if key != "socket":
            validation=json.loads((PUBLIC/key/"validation.json").read_text())
            assert validation["model_sha256"]==info["sourceSha256"]
            base_vertices = np.frombuffer(baseline, "<f4", count=meta["vertexByteLength"]//4).reshape(-1,8)
            study_vertices = np.frombuffer(data, "<f4", count=info["vertexByteLength"]//4).reshape(-1,8)
            xy_error = float(np.abs(study_vertices[:,:2] - base_vertices[:,:2]).max())
            if xy_error > 2e-6 or not np.array_equal(base_vertices[:,6:8],study_vertices[:,6:8]):
                raise ValueError("The height study changed horizontal geometry or the fixed UVs")
            evidence[key]["max_exported_horizontal_position_error"] = xy_error
            patch=exact_patch(baseline,data)
            tag="base-patch-"+key
            tags.append('<script id="'+tag+'" type="application/octet-stream">'+base64.b64encode(patch).decode("ascii")+'</script>')
            public[key]["patch"]=tag
            evidence[key]["patch_bytes"]=len(patch)
    atlas=(ROOT/material["texture"]).read_bytes()
    assert sha(atlas)==material["texture_sha256"]
    html=make_document(meta,baseline,atlas,studies=public,payload="\n".join(tags))
    html=html.replace('href="models/queen/queen-rebuilt.blend"','href="../../models/queen-base-studies/socket.blend"')
    html=html.replace("Starts at the overlay camera. Drag to explore.","Drag to orbit. Switching bases keeps your viewing angle.")
    html=html.replace('<div class="group" aria-label="Surface preview">','<div class="group" aria-label="Surface preview" style="display:none">')
    out=PUBLIC/"orbit-compressed.html"
    tmp=out.with_suffix(".html.tmp")
    tmp.write_text(html,encoding="utf-8",newline="\n")
    tmp.replace(out)
    registration=json.loads((ROOT/"assets/queen/original-reference-alignment.json").read_text())
    page=ROOT/"queen-bases.html"
    markup=page.read_text(encoding="utf-8")
    markup,count=re.subn(r'(<script id="study-registration" type="application/json">).*?(</script>)',
                         lambda m:m[1]+json.dumps(registration,separators=(",",":"))+m[2],markup,flags=re.S)
    assert count==1
    page.write_text(markup,encoding="utf-8",newline="\n")
    (PUBLIC/"mesh-check.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("Base viewer built from two verified Blender exports",out.stat().st_size,flush=True)


if __name__=="__main__":
    main()
