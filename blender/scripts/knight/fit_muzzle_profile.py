"""Fit the blunt conical muzzle to registered sprite boundaries with a locked camera."""
from pathlib import Path
import argparse
import json
import numpy as np
from lower_carving_fit import rest_coords, ease
from mission_pose import posed

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight"
BUILD=ROOT/"build/knight-mission"


def muzzle_shape(rest,params):
    advance,lift,drop,width=params
    result=rest.copy();x,y,z=rest.T
    head=ease(z,3.04,3.42)*ease(x,.44,.78)
    taper=ease(x,.65,1.69)*head
    under=1-ease(z,4.48-.53*x-.18,4.48-.53*x+.12)
    result[:,0]+=advance*taper
    result[:,2]+=lift*taper-drop*np.exp(-((x-.97)/.35)**2)*under*head
    result[:,1]*=1+width*head*np.exp(-((x-1.39)/.48)**2)
    return result


def carved_profile(rest,curve,width,depth,lower_rim):
    x,y,z=rest.T
    # A signed distance from the curved incision in the horse's side profile.
    center=np.interp(x,curve[:,0],curve[:,2])
    slopes=np.gradient(curve[:,2],curve[:,0])
    grad=np.interp(x,curve[:,0],slopes)
    signed=(z-center)/np.sqrt(1+grad**2)
    length=curve[-1,0]-curve[0,0]
    endcap=ease(x,curve[0,0]-.012,curve[0,0]+min(.09,length*.24))
    endcap*=1-ease(x,curve[-1,0]-min(.05,length*.18),curve[-1,0]+.016)
    side=ease(np.abs(y),.08,.19)
    hollow=-depth*np.exp(-.5*(signed/width)**2)
    rolled=lower_rim*np.exp(-.5*((signed+width*1.65)/(width*.8))**2)
    upper=.33*lower_rim*np.exp(-.5*((signed-width*1.55)/(width*.92))**2)
    return endcap*side*(hollow+rolled+upper)


def main():
    from PIL import Image
    from audit_mission import registered
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    opt=p.parse_args();opt.out.parent.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ASSETS/"mesh.json").read_text());camera=meta["referenceCamera"]
    mat=np.reshape(camera["projectionMatrix"],(4,4))@np.reshape(camera["worldToCamera"],(4,4))
    def screen(points):
        ndc=points@mat[:2,:3].T+mat[:2,3]
        return (1+ndc*[1,-1])*1254/2
    pose=json.loads((ROOT/"docs/knight-mission/iteration-001/001-carving-pose-pose.json").read_text())
    pp=[pose[k] for k in ("dx","dy","twist_degrees")]
    part=next(p for p in meta["parts"] if p["name"].endswith("continuous horse head and neck"))
    vertices=np.fromfile(ASSETS/"mesh.bin",dtype="<f4",count=meta["vertexCount"]*8).reshape(-1,8)
    idx=part["vertexOffset"];world=np.unique(vertices[idx:idx+part["vertexCount"],:3],axis=0)
    rest=rest_coords(world.astype(float),pp);x,y,z=rest.T
    rest=rest[(x>.46)&(z>np.maximum(3.22,4.22-.54*x-.38))]
    column=np.arange(592,717,4);row=np.arange(452,515,4)
    def from_cloud(params):
        a=screen(posed(muzzle_shape(rest,params),*pp))
        def reduce(ids,val,maximum,length):
            good=(ids>=0)&(ids<length)
            out=np.full(length,-np.inf if maximum else np.inf)
            (np.maximum if maximum else np.minimum).at(out,ids[good],val[good])
            finite=np.isfinite(out)
            return np.interp(np.arange(length),np.flatnonzero(finite),out[finite])
        cols=np.floor((a[:,0]-column[0]+2)/4).astype(int)
        rows=np.floor((a[:,1]-row[0]+2)/4).astype(int)
        return np.r_[reduce(cols,a[:,1],False,len(column)),reduce(cols,a[:,1],True,len(column)),reduce(rows,a[:,0],True,len(row))]
    def boundaries(image,source):
        a=np.asarray(image);m=a[:,:,3]>127
        if source:m&=a[:,:,:3].max(2)>12
        upper=[];lower=[];right=[]
        for col in column:
            ys=np.flatnonzero(m[330:575,col])+330
            blocks=np.split(ys,np.flatnonzero(np.diff(ys)>1)+1)
            head=blocks[0];upper.append(min(head));lower.append(max(head))
        for r in row:right.append(np.flatnonzero(m[r])[-1])
        return np.r_[upper,lower,right]
    refs=registered()
    targets=.83*boundaries(refs["original"],True)+.17*boundaries(refs["selected"],True)
    current=boundaries(Image.open(ASSETS/"render.png").convert("RGBA"),False)
    initial=from_cloud([0]*4)
    def loss(v):
        predicted=current+from_cloud(v)-initial
        # Ignore a column where the head and chest are already touching.
        mask=np.r_[np.ones(len(column),bool),(current[len(column):2*len(column)]<550)&(targets[len(column):2*len(column)]<550),np.ones(len(row),bool)]
        delta=np.abs(predicted[mask]-targets[mask])
        return float(np.mean(np.minimum(delta,23))+np.sum(np.abs(v)*[.7,1.3,1.0,1.4]))
    values=np.zeros(4);start=best=loss(values)
    for step in (.04,.016,.006,.002):
        for _ in range(16):
            before=best
            for i in range(4):
                for sign in (-1,1):
                    trial=values.copy();trial[i]+=sign*step
                    if any(abs(trial)>[.095,.14,.16,.15]):continue
                    error=loss(trial)
                    if error<best-.0001:values,best=trial,error
            if best==before:break
    record={"source_sha256":meta["sourceSha256"],"pose":pp,"advance_lift_underdrop_width":values.tolist(),
        "original_weight":.83,"initial_boundary_loss":start,"proxy_boundary_loss":best,
        "method":"Fit only the conical muzzle and lower jaw envelope. Keep the ears, eye, neck, pedestal, maximum height and saved camera."}
    opt.out.write_text(json.dumps(record,indent=2)+"\n");print(json.dumps(record))


if __name__=="__main__":main()
