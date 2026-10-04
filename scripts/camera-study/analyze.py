"""Reproduce original-image camera estimates and annotated comparison figures."""
from pathlib import Path
import argparse,json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from ellipse import fit

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--sources',type=Path,help='Optional separate root containing original references.')
args=parser.parse_args();root=args.root;source=args.sources or root;out=root/'docs/camera-study'
data=json.loads((out/'measurements.json').read_text());traces=[]
angles=np.arange(35,80.001,.25)
for t in data['features']:
 assert hashlib.sha256((source/t['file']).read_bytes()).hexdigest()==t['sha256'],t['file']
 t={**t,'independent_fit':fit(t['points'])}
 initial=[t['independent_fit'][k] for k in ['cx','cy','rx','ry']]
 t['profile']=[{'angle':float(a),**fit(t['points'],a,initial)} for a in angles]
 traces.append(t)
def pooled(weights):
 losses=[sum(w*t['profile'][i]['rms_px']**2 for w,t in zip(weights,traces))/sum(weights) for i in range(len(angles))]
 index=int(np.argmin(losses));return float(angles[index]),losses
best,losses=pooled([t['weight'] for t in traces])
sensitivity={}
for partial in [0,.1,.25,.5,1]:
 a,_=pooled([1 if t['piece']=='Rook' else partial for t in traces]);sensitivity[str(partial)]=a
report={'best_shared_elevation_degrees':best,'practical_interpretation':'About 54 degrees; roughly 50–58 is a working systematic bracket, not a statistical confidence interval. The previous 51.5/52-degree cameras remain compatible with this study.',
 'partial_arc_weight_sensitivity':sensitivity,'assumptions':data['projection_assumption'],
 'method':'Minimize weighted mean squared approximate orthogonal edge residual, with separate ellipse centers/radii for each feature and a shared minor/major ratio sin(elevation). A full ring carries weight 1; partially hidden front arcs weight 0.25. Weights are explicit engineering choices, not statistical inverse variances.',
 'traces':traces,'profile':[dict(angle=float(a),weighted_mean_squared_residual=float(v)) for a,v in zip(angles,losses)]}
(out/'fits.json').write_text(json.dumps(report,indent=2)+'\n')

def font(size,bold=False):
 paths=['C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),'/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold.ttf' if bold else '.ttf')]
 for path in paths:
  try:return ImageFont.truetype(path,size)
  except OSError:pass
 return ImageFont.load_default(size=size)

order=['King','Queen','Bishop','Knight','Rook','Pawn']
for mode in ['shared','independent']:
 can=Image.new('RGB',(1350,1170),'#11161d');d=ImageDraw.Draw(can)
 title='One shared viewing angle: 54° above the board' if mode=='shared' else 'Independent best fits — several angles are poorly constrained'
 d.text((28,15),title,font=font(30,True),fill='#f3eee5')
 d.text((28,58),'Untouched original sprites. Orange dots: sampled edges. Cyan dashes: fitted circles, including hidden portions.',font=font(17),fill='#aeb9c6')
 for i,piece in enumerate(order):
  t=next(t for t in traces if t['piece']==piece);f=t['independent_fit'] if mode=='independent' else next(p for p in t['profile'] if p['angle']==54)
  x=(i%3)*450;y=100+(i//3)*510
  d.rounded_rectangle((x+12,y,x+438,y+495),radius=12,fill='#1a222c')
  d.text((x+28,y+13),piece,font=font(24,True),fill='#eee8dc')
  label=f'{f["elevation_degrees"]:.0f}° — '+('stronger rim constraint' if piece=='Rook' else 'weak / partly hidden ring')
  d.text((x+28,y+45),label,font=font(16),fill='#9bdcf0')
  im=Image.open(source/t['file']).convert('RGBA');back=Image.new('RGBA',(300,300),'#10151b');back.alpha_composite(im)
  # Annotate on a larger analysis canvas; original source file is never rewritten.
  large=back.convert('RGB').resize((1200,1200),Image.Resampling.NEAREST);dr=ImageDraw.Draw(large)
  cx,cy,rx,ry=[f[k] for k in ['cx','cy','rx','ry']]
  for start in np.arange(0,2*math.pi,.12):
   ts=np.linspace(start,start+.065,8);dr.line([(4*(cx+rx*np.cos(a)),4*(cy+ry*np.sin(a))) for a in ts],fill='#66deed',width=3)
  for px,py in t['points']:dr.ellipse((4*px-2.5,4*py-2.5,4*px+2.5,4*py+2.5),fill='#ffb969')
  crop=large.crop((80,0,840,1080)).resize((285,405),Image.Resampling.LANCZOS);can.paste(crop,(x+82,y+72))
  d.text((x+28,y+472),f'Visible-edge residual: {f["rms_px"]:.2f} original pixels',font=font(14),fill='#9daabb')
 d.text((28,1137),'A good visible-arc fit does not recover the hidden circle uniquely. No generated candidates or model geometry used.',font=font(17),fill='#c0c6cf')
 can.save(out/f'{mode}-ellipses.png')

# A compact residual plot makes partial-arc ambiguity visible without treating fit error as confidence.
palette={'King':'#ed9b5e','Queen':'#ce9aeb','Bishop':'#80cca0','Knight':'#70b4ff','Rook':'#fff0a0','Pawn':'#f095ab'}
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 1100 650"><rect width="1100" height="650" fill="#11161d"/><g font-family="sans-serif" fill="#e6e9ed">',
 '<text x="75" y="40" font-size="26">Which angles fit the visible edges?</text><text x="75" y="69" font-size="17" fill="#aeb9c6">Lower is better. Flat curves indicate weak angle constraints.</text>']
sx=lambda a:75+(a-40)/30*890
sy=lambda r:530-r/1.0*420
for a in range(40,71,5):svg.append(f'<path d="M{sx(a)} 110V530" stroke="#2c3643"/><text x="{sx(a)-12}" y="555" font-size="15">{a}°</text>')
for r in np.arange(0,1.001,.2):svg.append(f'<path d="M75 {sy(r)}H965" stroke="#2c3643"/><text x="25" y="{sy(r)+5}" font-size="15">{r:.1f}</text>')
for t in traces:
 points=' '.join(f'{sx(p["angle"]):.2f},{sy(min(1,p["rms_px"])):.2f}' for p in t['profile'] if 40<=p['angle']<=70)
 svg.append(f'<polyline points="{points}" stroke="{palette[t["piece"]]}" stroke-width="3" fill="none"/>')
svg.append(f'<path d="M{sx(best)} 110V530" stroke="#ffffff" stroke-dasharray="6 7" opacity=".6"/><text x="{sx(best)+8}" y="130" font-size="16">shared ≈54°</text>')
for i,piece in enumerate(order):svg.append(f'<circle cx="{95+i*150}" cy="604" r="5" fill="{palette[piece]}"/><text x="{107+i*150}" y="610" font-size="17">{piece}</text>')
svg.append('<text x="335" y="579" font-size="17">Camera elevation above the board</text><text x="76" y="98" font-size="14">RMS edge error in original pixels</text></g></svg>')
(out/'angle-residuals.svg').write_text(''.join(svg),encoding='utf-8')
rows=''.join(f'<tr><td>{piece}</td><td>{next(t for t in traces if t["piece"]==piece)["independent_fit"]["elevation_degrees"]:.1f}°</td><td>{"Moderate: several rim sectors" if piece=="Rook" else "Low: hidden center / partial arc"}</td></tr>' for piece in order)
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shared camera study · listaunton</title><style>
:root{color-scheme:dark;font:16px/1.6 system-ui;background:#11161d;color:#e8edf2}body{max-width:1160px;margin:36px auto;padding:0 22px}a{color:#8ed8ed}h1{font-size:34px;line-height:1.2;margin-bottom:12px}p{max-width:850px;color:#b7c2ce}strong{color:#f6f0df}figure{margin:16px 0 28px}img{width:100%;height:auto;display:block;border-radius:12px}.switch{display:flex;gap:18px;align-items:center;margin-top:24px}.switch label{cursor:pointer}.switch input{accent-color:#8ed8ed}body:has(#independent:checked) #shared-figure,body:has(#shared:checked) #independent-figure{display:none}table{border-collapse:collapse;width:100%;max-width:760px;margin:20px 0}td,th{text-align:left;border-bottom:1px solid #35414e;padding:10px}th{color:#90cfe2}small{color:#9eacba}details{margin:22px 0}summary{cursor:pointer;font-weight:600}@media(max-width:620px){body{padding:0 12px;margin:20px auto}h1{font-size:27px}td,th{padding:7px;font-size:14px}}
</style></head><body><a href="index.html">← All pieces</a><h1>One camera across the set?</h1><p><strong>About 54° above the board</strong> is the combined working estimate. The rook supplies the clearest constraint; the other original images are compatible with it. A practical bracket is roughly <strong>50–58°</strong>, not a statistical confidence interval.</p><p>All measurements here use original 300px Lichess sprites. No generated candidates or reconstructed models determined this fit. Dashed back arcs are inferred, not visible evidence.</p>
<div class="switch"><label><input id="shared" type="radio" name="mode" checked> Shared 54°</label><label><input id="independent" type="radio" name="mode"> Independent fits</label></div>
<figure id="shared-figure"><img src="docs/camera-study/shared-ellipses.png" alt="The six original white pieces with a shared 54-degree circular projection fitted to their visible ring edges"></figure><figure id="independent-figure"><img src="docs/camera-study/independent-ellipses.png" alt="Independent ellipse fits diverge mainly in their hidden arcs, despite nearly matching the same visible edges"></figure>
<p>Independent fitting can select a very different angle while improving the visible arc by only a tiny fraction of one original pixel. These values are <strong>curve-fitting optima, not evidence of six different cameras</strong>.</p><table><thead><tr><th>Piece</th><th>Independent optimum</th><th>Reliability</th></tr></thead><tbody>__ROWS__</tbody></table>
<p>The current queen uses 51.5° and the king uses 52°. Both remain consistent with this study. Their 0.5° camera difference does not explain a substantial difference in modeled proportions. No model or existing review page was changed.</p>
<details><summary>Why most pieces cannot pin down the angle</summary><p>Only part of a circle is visible on most collars. Moving the inferred center and changing its radius allows many complete ellipses to match the same short arc. Bevel highlights, shadows, rounded profiles and original raster blur add systematic uncertainty. Significant perspective would also require a fuller camera model.</p><img src="docs/camera-study/angle-residuals.svg" alt="Error versus angle: the rook has a pronounced minimum near 54 degrees; the other pieces have much flatter curves"><p>The joint calculation gives each circle its own center and radius, but one shared minor/major ratio. The rook receives weight 1 and each partial arc 0.25. These are explicit reliability choices, not a statistical confidence model. Rounded outer collar silhouettes were excluded.</p></details>
<p><a href="docs/camera-study/REPORT.md">Study notes</a> · <a href="docs/camera-study/measurements.json">Source points and hashes</a> · <a href="docs/camera-study/fits.json">Fits and sensitivity</a></p></body></html>'''
(root/'camera-study.html').write_text(html.replace('__ROWS__',rows),encoding='utf-8')
print(json.dumps({'best_shared_degrees':best,'sensitivity':sensitivity,'independent':{t['piece']:round(t['independent_fit']['elevation_degrees'],2) for t in traces}},indent=2))
