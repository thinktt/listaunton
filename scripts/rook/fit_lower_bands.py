"""Local display-residual pigment fitting through real surface correspondence."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=ROOT/'history/rook-mission-063/assets/rook/pigment.png';assert sha(source)=='2e0d31a5446fb330f6935d40fcbeda8be659d3faf10215cbd808120709ea59e8'
m=np.load(ROOT/'build/rook-mission/064-lower-correspondence/mapping.npz');x,y=m['x'],m['y'];x0,y0,x1,y1=m['box'];valid=np.isfinite(x)&np.isfinite(y);x=np.nan_to_num(x);y=np.nan_to_num(y)
def sample(path):
 a=np.asarray(Image.open(path).convert('RGB'),dtype=float);ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy;assert ix.min()>=0 and iy.min()>=0 and ix.max()+1<a.shape[1] and iy.max()+1<a.shape[0];return (a[iy,ix]*(1-fx[:,:,None])+a[iy,ix+1]*fx[:,:,None])*(1-fy[:,:,None])+(a[iy+1,ix]*(1-fx[:,:,None])+a[iy+1,ix+1]*fx[:,:,None])*fy[:,:,None]
ref=sample(ROOT/'assets/rook/ref.png');current=sample(ROOT/'history/rook-mission-063/assets/rook/render.png');a=np.asarray(Image.open(source).convert('RGB'),dtype=float);h,w=a.shape[:2];U,V=np.meshgrid((np.arange(x0,x1)+.5)/w,1-(np.arange(y0,y1)+.5)/h);q1=((U-.56)/.060)**2+((V-.430)/.012)**2;q2=((U-.5643)/.045)**2+((V-.366)/.013)**2;mask=np.clip((2-np.minimum(q1,q2))/.8,0,1);mask=mask*mask*(3-2*mask)*valid
probe=json.loads((ROOT/'build/rook-mission/054-lower-probe/probe.json').read_text());errors=[]
for p in probe['samples']:
 u,v=p['uv'];i=int(u*w)-x0;j=int((1-v)*h)-y0
 if 0<=i<x.shape[1] and 0<=j<x.shape[0] and valid[j,i]:errors.append(float(np.hypot(x[j,i]-p['pixel'][0],y[j,i]-p['pixel'][1])))
assert errors and max(errors)<2,errors
for n,gain in [(65,.7),(66,1.0)]:
 out=ROOT/f'build/rook-mission/{n:03d}-local-pigment';out.mkdir(parents=True,exist_ok=True);result=a.copy();result[y0:y1,x0:x1]+=mask[:,:,None]*(ref-current)*gain;result=np.clip(result,0,255).round().astype(np.uint8);Image.fromarray(result).save(out/'pigment.png');outside=np.ones(a.shape[:2],bool);outside[y0:y1,x0:x1]=mask==0;report={'gain':gain,'source_atlas_sha256':sha(source),'reference_sha256':sha(ROOT/'assets/rook/ref.png'),'baseline_render_sha256':sha(ROOT/'history/rook-mission-063/assets/rook/render.png'),'unmasked_pixels_exact':bool(np.array_equal(result[outside],a.astype(np.uint8)[outside])),'max_probe_reprojection_error_pixels':max(errors),'method':'Approximate display-RGB residual added to local pigment using measured UV-to-camera correspondence. Preserves real BSDF; not physical albedo recovery. Includes reference detail and may inherit illumination.'};(out/'parameters.json').write_text(json.dumps(report,indent=2)+'\n');print(n,report)

