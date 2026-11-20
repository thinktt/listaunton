"""Compare the approved references and real fixed renders using identical image registration."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import black,registered
BOX=(448,444,565,524)
def normal(im):return np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)),dtype=float)@np.array([.2126,.7152,.0722])
def crop_lum(l,b):
    x,y,a,c=b
    return l[y-BOX[1]:c-BOX[1],x-BOX[0]:a-BOX[0]]
def metrics(im,ref):
    a=normal(im);b=normal(ref)
    out={}
    for label,box in [('inner_eye',(466,461,553,489)),('lower_lid',(463,488,548,512))]:
        aa=crop_lum(a,box).ravel();bb=crop_lum(b,box).ravel()
        out[label]={'correlation_black2':round(float(np.corrcoef(aa,bb)[0,1]),4),'luma_mae_black2':round(float(abs(aa-bb).mean()),2)}
    line=np.median(a[:,508-BOX[0]:517-BOX[0]],axis=1)
    trace={}
    for label,lo,hi,peak in [('inside',476,483,True),('separation',483,487,False),('second_arc',487,494,True),('lower_cheek',496,506,True)]:
        v=line[lo-BOX[1]:hi-BOX[1]+1];i=int(v.argmax() if peak else v.argmin())
        trace[label]={'y':lo+i,'luma':round(float(v[i]),1)}
    out['trace_x508_516']=trace
    out['arc_above_intervening_min']=round(trace['second_arc']['luma']-trace['separation']['luma'],1)
    return out
