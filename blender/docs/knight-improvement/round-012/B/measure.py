"""Measure the native junction, physical depth and outer contour at the accepted camera."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,sculpt,MANE,HEAD,sha
from probe_carving import point_probe
TARGET=np.array([[460,276],[475,269],[490,264],[505,263],[520,263],[535,264],[550,266],
                 [565,268],[580,272],[595,276],[610,280],[625,285],[640,288]])

def sample(s):
    probe=point_probe(s);record=[]
    for row,targ in TARGET:
        xs=np.arange(174,416);dist=np.full(len(xs),np.nan);nm=[]
        for i,x in enumerate(xs):
            hit=probe(x+.5,row+.5)
            nm.append(hit[1].replace('Knight | ','') if hit else '')
            if hit:dist[i]=hit[0]
        mane=xs[np.array(nm)==MANE]
        # Distance toward the object, relative to a straight chord from
        # the left face to the anterior neck. The crest on this curve is
        # a real recess along the camera ray, independent of illumination.
        if not len(mane):continue
        left=int(mane.min());edge=int(mane.max())
        lo=max(left+5,int(targ)-25);hi=int(targ)+70
        start,end=np.interp([lo,hi],xs,dist)
        chord=np.interp(xs,[lo,hi],[start,end])
        depth=dist-chord;reg=(xs>=lo+6)&(xs<=hi-6)
        xdeep=int(xs[reg][np.nanargmax(depth[reg])])
        record.append({'row':int(row),'source_x':int(targ),'back_x':left,'joint_x':edge,
            'peak_x':xdeep,'peak_recess':round(float(depth[xs==xdeep][0]),4),
            'depth_at_target':round(float(depth[xs==targ][0]),4),'xs':xs[reg].tolist(),
            'recess':np.round(depth[reg],5).tolist()})
    return {'rows':record,'joint_mean_error':float(np.mean([abs(v['joint_x']-v['source_x']) for v in record])),
            'peak_mean_error':float(np.mean([abs(v['peak_x']-v['source_x']) for v in record]))}

if __name__=='__main__':
    for key in sys.argv[sys.argv.index('--')+1:]:
        s=load('knight.blend' if key=='knight' else 'parent.blend')
        if key.isdigit():sculpt(s,int(key))
        r=sample(s)
        if key in ('knight','parent'):r['source_sha256']=sha(D/(key+'.blend'))
        print(key,r['joint_mean_error'],r['peak_mean_error'],[(v['row'],v['back_x'],v['joint_x'],v['peak_recess']) for v in r['rows'][::3]],flush=True)
        (D/f'sections-{key}.json').write_text(json.dumps(r,indent=2)+'\n')
