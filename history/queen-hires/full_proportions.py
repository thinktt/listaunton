"""A coherent, fuller queen rather than compensating base compression in the stem."""
import ast
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
out=root/'outputs'/'queen-hires'
work=root/'work'/'queen-hires'
source=(work/'before-fuller-proportions'/'build_queen.py').read_text()
tree=ast.parse(source)
values={}
for node in tree.body:
    if isinstance(node,ast.Assign):
        for name in ('body_profile','features'):
            if any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
                values[name]=ast.literal_eval(node.value)

anchor=.482
upper=2.916
factor=.85
drop=(upper-anchor)*(1-factor)

def lerp(knots,z):
    if z<=knots[0][0]: return knots[0][1]
    for (a,b),(c,d) in zip(knots,knots[1:]):
        if z<=c: return b+(d-b)*(z-a)/(c-a)
    return knots[-1][1]

flare_bonus=[(.482,0),(.500,.003),(.523,.012),(.551,.025),
             (.585,.038),(.623,.045),(.65807142,.06019681),
             (.72229826,.06490370),(.80227885,.05723681),
             (.88468309,.040),(.91355007,.030),(.94825917,.024),
             (1.18022593,.024),(1.362,.01935)]

def shape(r,z):
    zz=z if z<=anchor else anchor+factor*(z-anchor) if z<upper else z-drop
    # Lift the collar stack .06 within the shorter upper assembly to fit the
    # source arcs at the refitted camera. This shortens the tapered crown body.
    if 2.15<z<upper:
        zz+=.06*(z-2.15)/(upper-2.15)
    elif upper<=z<=3.384:
        zz+=.06
    elif 3.384<z<4.102:
        zz+=.06*(4.102-z)/(4.102-3.384)
    if z<=anchor or z>=upper:
        rr=r
    elif z<=1.362:
        rr=r+lerp(flare_bonus,z)
    else:
        rr=r*(1+lerp([(1.362,.05),(2.455,.12),(upper,0)],z))
    return rr,zz

new=[shape(r,z) for r,z in values['body_profile']]
assert new[:values['body_profile'].index((1.014,.482))+1]==values['body_profile'][:values['body_profile'].index((1.014,.482))+1]
lines=[''.join(f'({r:.8f},{z:.8f}),' for r,z in new[i:i+4]) for i in range(0,len(new),4)]
start=source.index('body_profile=[')
end=source.index("body=lathe(",start)
source=source[:start]+'body_profile=[\n'+'\n'.join(lines)+']\n'+source[end:]
start=source.index('# Fresh profile derived')
end=source.index('body_profile=[',start)
source=source[:start]+'''# Fuller proportions: compress the lower flare and socket, shorten the stem
# about 11%, and bring the upper assembly down. Fill the flare's middle, widen
# the socket modestly, and thicken the stem waist by 12%. The collar stack is
# lifted .06 within the lowered upper assembly, shortening the crown body.
# Foot, shallow groove and crown shape remain. Camera is refitted to 51.5deg.
UPPER_DROP=.3651
'''+source[end:]
needle="crown=mesh('02 Crown - rolled scallops, shallow scoop and egg finial',vs,fs)"
assert source.count(needle)==1
source=source.replace(needle,needle+'\ncrown.location.z=-UPPER_DROP')
features={key:shape(r,z) for key,(r,z) in values['features'].items()}
start=source.index('features={')
end=source.index("(OUT/'profile-landmarks.json')",start)
source=source[:start]+'features={\n'+''.join(f" '{name}':({r:.8f},{z:.8f}),\n" for name,(r,z) in features.items())+'}\n'+source[end:]
source=source.replace('S=273.5; ELEV=55.32; CX=483.625; Y0=874.0;',
                      'S=273.5; ELEV=51.5; CX=483.625; Y0=880.0;')
(out/'build_queen.py').write_text(source)
old_h=4.495-.219
new_h=4.495-drop-.219
report={'stem_height_reduction_percent':100*(1-(shape(.415,2.916)[1]-shape(.387,1.362)[1])/(2.916-1.362)),
        'crown_body_height_reduction_percent':100*.06/(4.102-3.384),
        'lower_assembly_height_reduction_percent':100*(1-(shape(.387,1.362)[1]-.219)/(1.362-.219)),
        'overall_height_reduction_percent':100*(1-new_h/old_h),'upper_assembly_translation_z':-drop,
        'stem_waist_radius_previous':.217,'stem_waist_radius_current':shape(.217,2.455)[0],
        'socket_wall_radius_current':shape(.520,1.10290368)[0],
        'foot_and_rounded_groove_unchanged':True,'crown_shape_unchanged':True,
        'camera':{'elevation':51.5,'scale':273.5,'cx':483.625,'y0':880.0},'features':features}
(work/'fuller-proportions-shape-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
