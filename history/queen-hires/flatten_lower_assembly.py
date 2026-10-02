"""Flatten the lower assembly while distributing the camera-fit error."""
import ast
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
out=root/'outputs'/'queen-hires'
backup=root/'work'/'queen-hires'/'before-base-flattening'
source=(backup/'build_queen.py').read_text()
tree=ast.parse(source)
profile=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='body_profile' for t in n.targets))
lo=.4348
join=1.490
shift=.128

def reshape(r,z):
    if z<=lo:
        zz=z+shift
    elif z<=join:
        zz=z+shift*(1-2*(z-lo)/(join-lo))
    elif z<2.15:
        zz=z-shift*(2.15-z)/(2.15-join)
    else:
        zz=z
    # Draft overlay showed the foot and rear base arc slightly too high.
    # Lower the flattened base a little, fading out before the upper socket.
    zz-=.035*max(0.,min(1.,(1.250-z)/(1.250-.906)))
    # Keep the wider socket cylindrical. Slightly broaden the foot, then
    # taper this correction to zero at the socket's lower wall.
    dr=.015*max(0.,min(1.,(1.006-z)/(1.006-lo))) if r>.01 else 0.
    return r+dr,zz

new=[reshape(r,z) for r,z in profile]
assert [p for p in profile if p[1]>=2.15]==[p for p in new if p[1]>=2.15]
new_lower=[p for p,old in zip(new,profile) if old[1]<2.15]
lines=[]
for i in range(0,len(new_lower),4):
    lines.append(''.join(f'({r:.8f},{z:.8f}),' for r,z in new_lower[i:i+4]))
start=source.index('body_profile=[')+len('body_profile=[')
end=source.index('(.251,2.15)',start)
source=source[:start]+'\n'+'\n'.join(lines)+'\n'+source[end:]
old_comment='''# Foot and broad base retain the 20% vertical compression about the foot groove.
# Socket is widened from r.465 to .520, with a higher rounded shoulder to bring
# its front arcs closer to the reference. The lower stem blends back at z2.15.'''
new_comment='''# Lower assembly shortened by 16.2%: foot raised .093 and socket join lowered
# .128, distributing the remaining overlay error instead of restoring height.
# Broad-base slope is 24.3% flatter; socket wall stays r.520 and rounds inward.
# Foot gains .015 radius; its flat edge is retained. Stem blends back at z2.15.'''
assert old_comment in source
source=source.replace(old_comment,new_comment)
for name,r,z in [('foot_groove',.9362,.358),('foot_lower_lip',1.01156,.2916),
                 ('base_shoulder',.98052,.4348),('socket_shoulder',.500,1.330),
                 ('stem_seat',.443,1.440)]:
    import re
    rr,zz=reshape(r,z)
    source,n=re.subn(r"('"+name+r"':)\([^)]*\)",rf'\g<1>({rr:.8f},{zz:.8f})',source)
    assert n==1
(out/'build_queen.py').write_text(source)
old_height=join-.126
new_height=reshape(.387,join)[1]-reshape(.001,.126)[1]
report={'previous_lower_height':old_height,'current_lower_height':new_height,
        'height_reduction_percent':100*(1-new_height/old_height),
        'socket_wall_radius':.520,'foot_wall_radius':1.037,
        'foot_bottom':reshape(.001,.126)[1],
        'socket_join':reshape(.387,join),
        'upper_profile_unchanged':True}
(root/'work'/'queen-hires'/'base-flattening-shape-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
