"""Constrained proposal: smaller lower turning with the original projection held."""
from pathlib import Path
import argparse,contextlib,io,json,math,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
with contextlib.redirect_stdout(io.StringIO()):
    from study_compact_family import ROOT,DOC,p,al,f,c,body,cap,widths,bias,ys,refwidth,changed
# Compress the lower turning by 12% above the existing groove. Collar spacing
# is adjusted independently. The preserved saw keeps the original slit line.
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant',choices=['a','b'],default='b');args=parser.parse_args()
names=['flare_bulge','upper_drop','upper_radius','head_drop','cap_radius','cap_rim_z','stem_radius','foot_width']
lower=np.array([.014,.038,.920,.012,.965,4.493,-.012,.005])
upper=np.array([.050,.060,.970,.040,1.010,4.508,.006,.018])
start=np.array([.035,.048,.945,.025,.985,4.505,.003,.012])
if args.variant=='a':
    lower[-1]=upper[-1]=start[-1]=0
    lower[5]=4.498;upper[5]=4.516;start[:7]=[.025,.048,.945,.025,.990,4.508,-.003]
def shape(v):
    bulge,drop,radius,head,cap_radius,rim,stem_radius,foot_width=v
    b,k=changed([.12,bulge,drop,radius,head,1,0])
    # The rounded button is shallower, with a genuine smooth crown. This
    # shortens the physical model without translating its image as a whole.
    k[:4,1]=cap[:4,1]-head
    if args.variant=='a':
        k[4:,1]=[rim-.025,rim-.007,rim+.004,rim+.010,4.529,4.533,4.534,4.534]
    else:
        k[4:,1]=[rim-.025,rim-.007,rim+.004,rim+.014,4.543,4.552,4.557,4.559]
    k[:,0]=cap[:,0]*cap_radius
    b[32:39,0]+=stem_radius*np.array([.2,.7,1,.9,.5,.1,0])
    b[:,0]*=1+foot_width*np.clip((1.02-body[:,1])/.52,0,1)
    return b,k
def objective(v,detail=False):
    b,k=shape(v);w=widths(b,k)+bias
    error=w-refwidth[ys]
    weights=np.ones(len(ys));weights[ys<215]=2.0;weights[(ys>=480)&(ys<615)]=1.3
    # Keep the source outline, especially the finial and collars. Do not
    # improve a global score by moving the tip or stretching reference images.
    loss=np.mean(weights*np.sqrt(error*error+.5))
    b0=widths(body,cap)+bias
    penalty=max(0,float(np.max(abs(error[ys<180])))-9)*.1
    smooth=np.diff(b[31:40,0],n=2)
    loss+=penalty+.03*np.square((v-start)/np.maximum(upper-lower,1e-8)).mean()+2*np.square(smooth).sum()
    if detail:
        return {'loss':float(loss),'height_control':float(max(b[:,1].max(),k[:,1].max())),
          'regions':{name:float(np.mean(abs(error[(ys>=lo)&(ys<hi)]))) for name,lo,hi in [('button',150,245),('head',245,480),('collars',480,615),('stem',615,705),('base',705,1118)]},
          'parameters':dict(zip(names,map(float,v)))}
    return float(loss)
v=start.copy()
for step in [.16,.08,.04,.02,.01]:
    for _ in range(5):
        did=False
        for j in range(len(v)):
            base=objective(v);choices=[]
            for sign in [-1,1]:
                q=v.copy();q[j]=np.clip(q[j]+sign*step*(upper[j]-lower[j]),lower[j],upper[j])
                choices.append((objective(q),q))
            score,q=min(choices,key=lambda row:row[0])
            if score<base-1e-7:v=q;did=True
        if not did:break
b,k=shape(v)
def encode(q):
    return np.column_stack((q[:,0]/f,p['y0']-q[:,1]*c/f))
bp=encode(b);kp=encode(k)
config={'variant':'187-compact-family-'+args.variant,'source':'history/bishop-mission-030/bishop-rebuilt.blend',
 'source_sha256':'2cebd2e24cbf773e7551d14f68cacf6d33a590c85dd249026e6221ea9afd2ba6',
 'profile':'history/bishop-mission-030/profile.json','samples':128 if args.variant=='b' else 64,
 'body_rings':{str(i):list(map(float,bp[i])) for i in range(len(body)) if np.max(abs(b[i]-body[i]))>1e-6},
 'finial_rings':{str(i):list(map(float,kp[i])) for i in range(len(cap)) if np.max(abs(k[i]-cap[i]))>1e-6},
 'head_cap_axis_y':float(bp[-1,1]),
 'intent':'Compress lower turning 12% above its groove and broaden its inner flare. Lower upper collar. Refit upper form at the same 54-degree camera with an explicitly shorter model; preserve reference pixels and registration.'}
(DOC/'compact-family.json').write_text(json.dumps(config,indent=2)+'\n',newline='\n')
(DOC/'fit-proposal.json').write_text(json.dumps({'method':'Calibrated sampled rotational-envelope prediction. Saved-file renders govern acceptance. No camera or image alignment changes.','start':objective(start,True),'fit':objective(v,True)},indent=2)+'\n',newline='\n')
print(json.dumps(objective(v,True),indent=2))
