"""Measure collar highlight location and grain against the fixed reference. Output path, then trial names."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/"scripts/pawn"))
from derive_wood import blur
images={"selected":r/"assets/pawn/reference.png","accepted-baseline":r/"assets/pawn/render.png"}
images.update({v:r/"build/pawn-mission"/v/"fixed.png" for v in sys.argv[2:]})
boxes={"left":[405,588,481,630],"right":[516,578,569,617],"front":[495,616,558,642]}
report={}
target=None
for name,path in images.items():
    im=np.asarray(Image.open(path).convert("RGB"),np.float64)
    if target is None:target=im
    stats={}
    for part,box in boxes.items():
        x0,y0,x1,y1=box
        rgb=im[y0:y1,x0:x1];v=rgb@np.array([.24,.53,.23]);y,x=np.mgrid[y0:y1,x0:x1]
        centers={}
        for q in (.65,.8,.9,.95):
            w=np.maximum(v-np.quantile(v,q),0)
            centers[str(q)]=[float((x*w).sum()/w.sum()),float((y*w).sum()/w.sum()),float(np.quantile(v,q))]
        want=target[y0:y1,x0:x1]@np.array([.24,.53,.23])
        fine=v-blur(v,r=2,passes=1);tf=want-blur(want,r=2,passes=1)
        stats[part]={"centers":centers,"mae":float(np.abs(v-want).mean()),"fine_rms":float(np.sqrt((fine*fine).mean())),"fine_correlation":float(np.corrcoef(fine.ravel(),tf.ravel())[0,1])}
    report[name]=stats
out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
for k,v in report.items():print(k,{p:{"center":s["centers"]["0.8"],"mae":round(s["mae"],2),"fine_corr":round(s["fine_correlation"],3)} for p,s in v.items()})
