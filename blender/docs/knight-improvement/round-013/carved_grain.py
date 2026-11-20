"""Compare wood figure on the broad face of the mane away from the carved edge."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
b=r/'build/knight-mission';out=b/f'round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import black,registered,silhouette
refs=registered();sources={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for code in codes:sources[code]=Image.open(b/f'improvement-{n:03}-{code}/wood.png')
for name,filename in [('Parent pigment','pigment.png'),('Parent polish','polish.png')]:
    path=out/'mane-passes-parent'/filename
    if path.is_file():sources[name]=Image.open(path)
original=Image.open(r/'assets/knight/original.png')
align=json.loads((r/'assets/knight/original-alignment.json').read_bytes())
factor=align['scale']*original.width/refs['selected'].width;ox=align['x']*3;oy=align['y']*3
extent=(-ox/factor,-oy/factor,(original.width-ox)/factor,(original.height-oy)/factor)
ref_shape=silhouette(refs['selected'],True)
track=json.loads((b/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples']
ty,tx=np.array([q[:2] for q in track]).T
height,width=ref_shape.shape
mask=np.zeros((height,width),bool)
for y in range(463,622):
    col=np.flatnonzero(ref_shape[y]);left=int(col[0]);right=np.interp(y,ty,tx);span=right-left
    mask[y,round(left+.20*span):round(left+.71*span)]=True
native_mask=np.asarray(Image.fromarray(mask).convert('L').resize(original.size,Image.Resampling.BILINEAR,box=extent))>220
w,h=164,220;palette='#e8e8dd';f=ImageFont.load_default(size=13)
sheet=Image.new('RGB',(w*len(sources),h*2+61),'#242824');d=ImageDraw.Draw(sheet)
measure={}
def channels(pic):return np.asarray(pic,dtype=float)@[.2126,.7152,.0722]
for i,(key,picture) in enumerate(sources.items()):
    rgb=black(picture.convert('RGBA'))
    native=black(original.convert('RGBA')) if key=='Original black' else rgb.resize(original.size,Image.Resampling.LANCZOS,box=extent)
    measure[key]={};x=i*w
    for tag,im,m,sig in [('reference_grid',rgb,mask,1.),('sprite_grid',native,native_mask,factor)]:
        raw=channels(im);bands={}
        for fine,broad in [(0.,2.),(2.,8.),(8.,16.)]:
            v=raw if fine==0 else channels(im.filter(ImageFilter.GaussianBlur(sig*fine)))
            avg=channels(im.filter(ImageFilter.GaussianBlur(sig*broad)))
            detail=v-avg;norm=detail/np.maximum(avg,12)
            bands[f'{fine:g}-{broad:g}']={'rms_luminance':round(float(np.sqrt(np.mean(detail[m]**2))),3),
                                         'relative_rms':round(float(np.sqrt(np.mean(norm[m]**2))),4)}
        # Direction from the structure tensor of the grain-scale band in the image plane.
        residual=channels(im.filter(ImageFilter.GaussianBlur(max(.4,1.5*sig))))-channels(im.filter(ImageFilter.GaussianBlur(8*sig)))
        dy,dx=np.gradient(residual);X,Y=dx[m],dy[m]
        spec,vec=np.linalg.eigh([[np.mean(X**2),np.mean(X*Y)],[np.mean(X*Y),np.mean(Y**2)]])
        vec=vec[:,0];angle=(np.degrees(np.arctan2(vec[1],vec[0]))+90)%180-90
        measure[key][tag]={'sample_pixels':int(m.sum()),'median_luminance':round(float(np.median(raw[m])),2),'band_details':bands,
                            'grain_direction_image_degrees':round(float(angle),1),'grain_coherence':round(float((spec[1]-spec[0])/max(1e-6,spec.sum())),3)}
    crop=(172,435,318,647)
    tile=rgb.crop(crop).resize((w-2,h),Image.Resampling.LANCZOS)
    sheet.paste(tile,(x,24));d.text((x+4,4),key,font=f,fill=palette)
    # Equal local-contrast gain helps reveal the direction of the grain across the mask.
    arr=channels(rgb);coarse=channels(rgb.filter(ImageFilter.GaussianBlur(8)))
    study=128+350*(arr-coarse)/np.maximum(coarse,12)
    disk=np.where(mask,study,40)
    preview=Image.fromarray(np.uint8(np.clip(disk,0,255))).crop(crop).resize((w-2,h),Image.Resampling.LANCZOS)
    sheet.paste(preview,(x,h+31))
d.text((5,2*h+39),'Lower row shows local wood contrast at equal gain.',font=f,fill=palette)
sheet.save(out/'mane-grain.png')
(out/'mane-grain.json').write_text(json.dumps({'method':'Within the face of the mane, mask out the exterior silhouette and interior hollow. Sample the middle of its width over rows 463–621. Compare luminance residual in three spatial bands after dividing by local mean intensity, and inspect the dominant image-plane grain direction and its coherence. The paired native-grid result resamples renders to the original 300px canvas; its first entry samples the actual original PNG. The high-resolution image is interpretive.','results':measure},indent=2)+'\n')
print({k:{grid:[v['band_details']['2-8']['relative_rms'],v['grain_direction_image_degrees'],v['grain_coherence']] for grid,v in grids.items()} for k,grids in measure.items()})
