"""Save fixed-registration source crops and collar residuals for examination."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from audit_mission import ROOT,BUILD,rgba,registered,black,sheet,sha

def run(folder):
    out=BUILD/folder;out.mkdir(parents=True,exist_ok=True)
    images=registered();images['current']=rgba(ROOT/'assets/pawn/render.png')
    sheet(list(images.items()),(370,535,592,650),420,out/'collar-context.png')
    sheet([(k,images[k]) for k in ['selected','current','original_black']],(389,590,481,641),420,out/'collar-detail.png')
    t=np.asarray(black(images['selected']),float);a=np.asarray(black(images['current']),float)
    x0,y0,x1,y1=389,590,481,641
    delta=(a-t)[y0:y1,x0:x1]@np.array([.24,.53,.23])
    heat=np.zeros((*delta.shape,3),np.uint8)
    heat[:,:,0]=np.clip(np.maximum(delta,0)*4,0,255);heat[:,:,2]=np.clip(np.maximum(-delta,0)*4,0,255)
    im=Image.fromarray(heat).resize((552,306),Image.Resampling.NEAREST)
    canvas=Image.new('RGB',(568,352),(22,24,27));canvas.paste(im,(8,38));draw=ImageDraw.Draw(canvas)
    draw.text((8,8),'Red: model brighter. Blue: reference brighter. Fixed registration.',fill='white')
    canvas.save(out/'signed-residual.png')
    report={'source_render_sha256':sha(ROOT/'assets/pawn/render.png'),'source_model_sha256':sha(ROOT/'models/pawn/pawn-rebuilt.blend'),
            'regions':{},'note':'Sources are unchanged, uniformly magnified only for inspection. White supplies additional form cues, not color matching.'}
    for name,box in {'left-outer':[389,606,421,638],'left-front':[425,606,457,638],'main-glint':[405,588,481,630]}.items():
        x0,y0,x1,y1=box;d=(a-t)[y0:y1,x0:x1]
        report['regions'][name]={'bounds':box,'rgb_mae_255':float(abs(d).mean()),'signed_mean_rgb':d.mean((0,1)).tolist()}
    (out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();run(a.folder)
