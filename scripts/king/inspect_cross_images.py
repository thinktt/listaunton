"""Compare both original cross sprites, selected black 1 and current render."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2];out=root/'build/king-mission/cross-inspection';out.mkdir(parents=True,exist_ok=True)
ref=Image.open(root/'assets/king/reference.png').convert('RGBA');cfg=json.loads((root/'assets/king/original-alignment.json').read_text());s,x,y=(cfg[k] for k in ['scale','x','y']);W=ref.width
originals=[Image.open(root/f'references/lichess-staunton-3d/{color}-King.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR) for color in ['Black','White']]
panel=Image.new('RGB',(4*440,500),(20,22,26));d=ImageDraw.Draw(panel);fontpath=next((p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists()),None);font=ImageFont.truetype(fontpath,18) if fontpath else ImageFont.load_default()
for i,(title,im) in enumerate(zip(['Original black','Original white','Selected black 1','Current model'],originals+[ref,Image.open(root/'assets/king/render.png').convert('RGBA')])):
    d.text((i*440+10,8),title,fill='white',font=font)
    image=Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB').crop((385,0,625,245)).resize((430,439),Image.Resampling.LANCZOS);panel.paste(image,(i*440+5,45))
panel.save(out/'cross-sources.png')
print(out/'cross-sources.png')
