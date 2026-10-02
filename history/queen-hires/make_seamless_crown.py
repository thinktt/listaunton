"""Join the accepted queen body directly into a pressed, splash-like crown."""
import ast
from pathlib import Path

root=Path(__file__).resolve().parents[2]
out=root/'outputs'/'queen-hires'
source=(root/'work'/'queen-hires'/'before-seamless-crown'/'build_queen.py').read_text()
tree=ast.parse(source)
values={}
for node in tree.body:
    if isinstance(node,ast.Assign):
        for name in ('body_profile','crown_profile'):
            if any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
                values[name]=ast.literal_eval(node.value)

profile=values['body_profile']
end=profile.index((.48320313,3.54445687))+1
profile=profile[:end]
start_text=source.index('body_profile=[')
end_text=source.index('# Semantic ring locations',start_text)
lines=[''.join(f'({r:.8f},{z:.8f}),' for r,z in profile[i:i+4]) for i in range(0,len(profile),4)]
new='body_profile=[\n'+'\n'.join(lines)+']\n\n'
new+='# Retained crown profile supplies the bowl, finial and tip maxima.\n'
new+='crown_profile='+repr(values['crown_profile'])+'\n'
new+='''
# One watertight surface: sole -> body -> flared rim -> bowl -> egg.
# The body keeps its original 192 angular samples exactly. The crown is
# resampled onto those shared rings; there are no overlapping caps or seams.
N=192
rings=[]
for r,z in body_profile:
 rings.append([(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for i in range(N)])
body_ring_count=len(rings)

# Gradually turn the straight taper outward before scalloping begins.
for r,z,w in ((.497,3.625,0),(.515,3.700,.02)):
 ring=[]
 for i in range(N):
  a=i*math.tau/N
  peak=((1+math.cos(8*(a-math.pi/8)))/2)**4.2
  rr=r+.090*w*peak
  zz=z+.099*w*peak
  ring.append((rr*math.cos(a),rr*math.sin(a),zz))
 rings.append(ring)

finial_first_ring=None
for j,(r,z,w) in enumerate(crown_profile):
 if j<3: continue # discard the old underside disk and overlapping closure
 if j==20: finial_first_ring=len(rings)
 ring=[]
 for i in range(N):
  a=i*math.tau/N
  exponent=4.2 if j<=9 else 3.8 if j==10 else 3.1
  peak=((1+math.cos(8*(a-math.pi/8)))/2)**exponent
  rr=r-.100*w+.090*w*peak
  zz=z+.125*w+.099*w*peak-UPPER_DROP
  if j<=7: zz+=.075*(1-w)**2
  valley=(1-peak)**2
  if j in (3,4,5):
   # A steadily increasing wall radius avoids a shelf below the pressed lip.
   # Both the base radius and the scallop amplitude flow into the rim.
   base_r,base_z={3:(.529,3.752),4:(.545,3.802),5:(.559,3.848)}[j]
   rr=base_r+.090*w*peak
   zz=base_z+.099*w*peak
  press=1.0 if 6<=j<=9 else .85 if j==10 else 0.
  if press:
   # A flatter band between points, retaining a small soft bevel.
   rr+=(.545-rr)*.30*valley*press
   zz+=(3.920-zz)*.50*valley*press
  ring.append((rr*math.cos(a),rr*math.sin(a),zz))
 rings.append(ring)

vs=[v for ring in rings for v in ring]
fs=[]
for j in range(len(rings)-1):
 for i in range(N):
  k=(i+1)%N
  fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
fs+=[tuple(reversed(range(N))),tuple((len(rings)-1)*N+i for i in range(N))]
queen=mesh('01 Queen - continuous body and splash crown',vs,fs)
m=queen.modifiers.new('Continuous carved surface','SUBSURF');m.levels=2;m.render_levels=2
queen['ring_segments']=N
queen['body_preserved_ring_count']=body_ring_count
queen['finial_first_ring']=finial_first_ring
queen['finial_ring_count']=len(crown_profile)-20
queen['finial_source_first_ring']=20
for name,start,end in (('Body and collars',0,body_ring_count*N),
                       ('Crown flare and bowl',(body_ring_count-1)*N,finial_first_ring*N),
                       ('Egg finial',finial_first_ring*N,len(vs))):
 group=queen.vertex_groups.new(name=name)
 group.add(list(range(start,end)),1.,'REPLACE')
scene['continuous_crown']=True
scene['crown_tip_count']=8

'''
source=source[:start_text]+new+source[end_text:]
source=source.replace('for ob in (body,crown):','for ob in (queen,):')
source=source.replace('body.select_set(True);crown.select_set(True);bpy.context.view_layer.objects.active=body',
                      'queen.select_set(True);bpy.context.view_layer.objects.active=queen')
source=source.replace('# Foot, shallow groove and crown shape remain. Camera is refitted to 51.5deg.',
                      '# Accepted lower proportions remain. Crown now flows into a seamless splash rim.')
source=source.replace("scene['reconstruction']='New profile from hi-res-queen.png; camera elevation fitted to eight crown points. Geometry review material; wood finish deferred.'",
                      "scene['reconstruction']='Fuller queen proportions; continuous splash crown with pressed rim valleys. Camera refitted to 51.5 degrees. Geometry review material; wood deferred.'")
ast.parse(source)
(out/'build_queen.py').write_text(source)
print(f'Continuous mesh: {len(profile)} preserved body rings, 192 shared angular samples.')
