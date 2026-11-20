"""Read unchanged queen references into a registered lighting-fit diagnostic."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageFont
W=Path(__file__).resolve().parent
R=next((p for p in W.parents if (p/'assets/queen').is_dir()),W.parent/'queen-profile-019');A=R/'assets/queen'
out=R/'build/queen-mission/contact-targets-021';out.mkdir(parents=True,exist_ok=True)
reg=json.loads((A/'original-reference-alignment.json').read_text());s,x,y=reg['scale'],reg['offset_x'],reg['offset_y']
original_path=R/'references/lichess-staunton-3d/Black-Queen.png';detail_path=A/'reference.png'
original=Image.open(original_path).convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-x/s,0,1/s,-y/s),Image.Resampling.BILINEAR)
selected=Image.open(detail_path).convert('RGBA');current=Image.open(R/'history/queen-mission-021/queen-brown.png').convert('RGBA')
crop=[415,239,552,293];box=(400,225,570,300)
def rgb(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB')
for label,im in [('original',original),('highres',selected)]:
    np.save(out/(label+'.npy'),np.asarray(rgb(im).filter(ImageFilter.GaussianBlur(2)).crop(crop),dtype=np.float32)/255)
font_path=next(p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists())
font=ImageFont.truetype(font_path,20)
sheet=Image.new('RGB',(1050,205),(22,25,31));d=ImageDraw.Draw(sheet)
for i,(label,im) in enumerate([('Original',original),('Selected high-res',selected),('Accepted 21',current)]):
    d.text((12+i*350,8),label,font=font,fill='white');sheet.paste(rgb(im).crop(box).resize((340,150),Image.Resampling.LANCZOS),(12+i*350,42))
sheet.save(W/'contact-baseline.png')
manifest={'crop':crop,'blur_radius':2,'original_weight':.7,'highres_weight':.3,'original_sha256':hashlib.sha256(original_path.read_bytes()).hexdigest(),'highres_sha256':hashlib.sha256(detail_path.read_bytes()).hexdigest(),'original_registration':reg,'method':'Unchanged source images, existing uniform registration, black background; two-pixel blur for lighting comparison only.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
config={'variant':'199-shadowed-contact-fit','source':'history/queen-mission-021/queen-rebuilt.blend','source_sha256':'6ac2fe2309b0e6046db892be11ffbb986059228341c3b7ea140956e792de8c48','capture':'build/queen-mission/finial-contact-surface-021','targets':'build/queen-mission/contact-targets-021','samples':256,'reference_weights':[.7,.3],'color':[1,.8,.6],'radius':.14,'cone':4,'distance':6,'receiver_parts':['turned-body'],'target_pixels':[[437,263],[448,271],[458,275],[471,278],[497,274],[510,267],[528,268]],'energy':1500,'power_gain_limit':4,'fit_steps':15}
(W/'199-shadowed-contact-fit.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
print('CONTACT_TARGETS_READY',crop)
