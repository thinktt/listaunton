"""Compare the visible cut, board-size expression and photographed lower cheek turn."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D=Path(__file__).resolve().parent
A=D.parents[2]/'assets/knight'
def read(path):return Image.open(path).convert('RGBA')
def rgb(image):
    canvas=Image.new('RGBA',image.size,'black');canvas.alpha_composite(image)
    return canvas.convert('RGB')
def upper(path):
    doc=json.loads(path.read_text());pts=np.array(doc['columns'])
    center=pts[(pts[:,0]>=495)&(pts[:,0]<=504)]
    return {'area_px':doc['visible_pixels'],'tail_x_ymin_ymax':pts[0].tolist(),
            'nose_x_ymin_ymax':pts[-1].tolist(),'median_upper_y_x495_to_504':float(np.median(center[:,1]))}
def glint(im):
    # Compare the middle of the lens-shaped light on the lower lip or cheek.
    # The local-high-pass profile rejects broad walnut tone changes.
    g=rgb(im).convert('L')
    smooth=np.asarray(g.filter(ImageFilter.GaussianBlur(1.5)),float)
    base=np.asarray(g.filter(ImageFilter.GaussianBlur(7)),float)
    residual=(smooth-base)[486:507,478:530]
    pos=np.unravel_index(int(np.argmax(residual)),residual.shape)
    seen={pos};todo=[pos]
    while todo:
        y,x=todo.pop()
        for j,i in ((y+1,x),(y-1,x),(y,x+1),(y,x-1)):
            if 0<=j<residual.shape[0] and 0<=i<residual.shape[1] and (j,i) not in seen and residual[j,i]>=residual[pos]*.5:
                seen.add((j,i));todo.append((j,i))
    py,px=np.array(sorted(seen)).T
    return {'peak_xy':[int(pos[1]+478),int(pos[0]+486)],'half_peak_width_height':[int(np.ptp(px)+1),int(np.ptp(py)+1)],
            'half_peak_centroid_xy':[round(float(px.mean()+478),2),round(float(py.mean()+486),2)]}
def main():
    black=read(A/'ref.png');parent=read(D/'parent-wood.png');new=read(D/'wood.png')
    last=read(D.parent/'improvement-008-A'/'wood.png');orig=read(A/'original.png')
    ac=json.loads((A/'original-alignment.json').read_text());s=ac['scale']*300/1254
    full=orig.transform(black.size,Image.Transform.AFFINE,(s,0,ac['x']*3,0,s,ac['y']*3),Image.Resampling.BILINEAR)
    views=[('Original',full),('Black 2',black),('8B parent',parent),('Previous 8A',last),('9A',new)]
    sheet=Image.new('RGB',(1560,570),'#232527');draw=ImageDraw.Draw(sheet)
    for i,(label,image) in enumerate(views):
        x=i*312
        draw.text((x+8,5),label,fill='white')
        roi=rgb(image).crop((451,448,558,519)).resize((299,198),Image.Resampling.BICUBIC)
        sheet.paste(roi,(x+6,22))
        native=orig if i==0 else image.transform(orig.size,Image.Transform.AFFINE,
            (1/s,0,-ac['x']*3/s,0,1/s,-ac['y']*3/s),Image.Resampling.BICUBIC)
        draw.text((x+8,227),'Native 300 px frame',fill='white')
        sheet.paste(rgb(native),(x+6,244))
    sheet.save(D/'native-eye.png')
    lamps={k:glint(im) for k,im in views[1:]}
    out={'parent':upper(D/'fixed-eye-parent.json'),'candidate':upper(D/'fixed-eye.json'),'lower_glint':lamps,
         'glint_method':'Largest positive local contrast in the registered lower-lid and cheek window x478..529, y486..506. The contiguous half-peak extent of that patch uses 1.5 px and 7 px Gaussian luminance. The glints come from the studio and grain as well as the shape.'}
    (D/'eye-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
