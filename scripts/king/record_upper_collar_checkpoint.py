"""Record the king's upper-collar study and verified checkpoint 013 evidence."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import black,mask
from record_socket_checkpoint import original_colors_contact

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def main():
    D=ROOT/'docs/king-mission/iteration-013';A=ROOT/'history/king-mission-012'
    O=ROOT/'build/king-mission/151-upper-right-placement'
    checks=read(D/'reproduction-checks.json');scope=read(D/'scope-check.json')
    for key in ('independent_saved_reproduction','repeat_saved_render'):
        assert checks[key]['maximum_channel_error_255']<=1 and checks[key]['alpha_exact']
    assert all(checks[k] for k in ('reproduction_mesh_exact','camera_export_exact','physical_bounds_exact'))
    if not (D/'render-before-reopen.png').exists():shutil.copy2(O/'wood.png',D/'render-before-reopen.png')
    shutil.copy2(O/'wood-reopened.png',O/'wood.png')
    hashes=read(ROOT/'docs/king-mission/iteration-012/source-hashes.json')
    assert all(sha(ROOT/k)==v for k,v in hashes.items());write(D/'source-hashes.json',hashes)
    assert sha(A/'king-rebuilt.blend')=='5aea5f80285948a8f2e765f5b626f8a72069f8074a743b16c9b7fe07e9c4f281'
    definitions=[
        ('143-upper-glint-placement',85,67,'rejected','Weak improvement to the left; the split reflection remains and right placement worsens.'),
        ('144-upper-glint-power',85,66,'rejected','More energy makes the misplaced double stripe conspicuous.'),
        ('145-upper-glint-breadth',85,65,'rejected','Broader/brighter lights exaggerate the double stripe.'),
        ('146-upper-wide-source',85,63,'rejected','Over-bright white streaks wash across the wrong part of the collar.'),
        ('147-upper-collar-curve',85,66,'rejected','The larger upper-curve adjustment blocks the intended left reflected ray.'),
        ('149-upper-collar-gentle-curve',85,68,'superseded','Gentler curve and a near-crest aim reduce the left double band; right highlight is still displaced.'),
        ('150-upper-collar-centered-reflections',85,68,'rejected','Increasing the gentler candidate lights adds brightness but worsens the right patch.'),
        ('151-upper-right-placement',85,69,'validated candidate','Gentler upper curve, less split left patch, and a corrected right aim. Remaining texture bands and imperfect highlight breadth are visible.')]
    trials=[]
    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');target=np.asarray(black(ref),dtype=float)
    base=Image.open(A/'render.png').convert('RGBA');old=np.asarray(black(base),dtype=float)
    common=mask(ref,True)&mask(base)
    boxes={'upper-collar':[370,400,650,453],'left-glint':[448,415,505,442],'right-glint':[530,411,588,440],'collars':[300,390,710,555]}
    regional={}
    for name,interior,lighting,decision,reason in definitions:
        T=ROOT/'build/king-mission'/name;E=D/'trials'/name;E.mkdir(parents=True,exist_ok=True)
        m=read(T/'metrics.json');scores=dict(silhouette_iou_percent=m['highres_iou']*100,interior_form=interior,wood_color=82,grain_surface=79,lighting_reflections=lighting)
        trials.append(dict(variant=name,scores=scores,equal_weight_mean=sum(scores.values())/5,original_iou_percent=m['original_iou']*100,decision=decision,reason=reason,model_sha256=sha(T/'king.blend'),render_sha256=sha(T/'wood-reopened.png')))
        for src,dest in [('wood-reopened.png','wood.png'),('metrics.json','metrics.json'),('turning.json','turning.json'),('parameters.json','parameters.json')]:shutil.copy2(T/src,E/dest)
        cfg=read(T/'input.json');cfg['source']='history/king-mission-012/king-rebuilt.blend';write(E/'input.json',cfg)
        actual=np.asarray(black(Image.open(T/'wood-reopened.png').convert('RGBA')),dtype=float);regional[name]={}
        for key,(x0,y0,x1,y1) in boxes.items():
            use=common[y0:y1,x0:x1];a=actual[y0:y1,x0:x1][use];b=old[y0:y1,x0:x1][use];r=target[y0:y1,x0:x1][use]
            regional[name][key]=dict(bounds=boxes[key],foreground_pixels=int(use.sum()),previous_rgb_mse=float(np.square(b-r).mean()),trial_rgb_mse=float(np.square(a-r).mean()))
    write(D/'scores.json',dict(rubric='Only silhouette IoU is measured; the other ratings are visual judgments with the unchanged mission rubric.',holistic_visual_range_percent=[75,85],trials=trials))
    write(D/'regional-measurements.json',dict(method='Composited RGB squared error on common foreground; not a perceptual-match percentage.',trials=regional))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','neutral.png','profile.png','rear.png','side.png','turning.json']:shutil.copy2(O/name,D/name)
    for folder in ['142-upper-collar-diagnostic','148-upper-normal-diagnostic']:
        E=D/folder;E.mkdir(exist_ok=True)
        for p in (ROOT/'build/king-mission'/folder).iterdir():
            if p.suffix in ('.png','.json'):shutil.copy2(p,E/p.name)
    shutil.copy2(ROOT/'build/king-mission/147-upper-collar-curve/normals.json',D/'larger-curve-normal-probes.json')
    original_colors_contact(D,O)
    sheet=Image.new('RGB',(1200,925),'#17191b');draw=ImageDraw.Draw(sheet)
    for i,(label,p) in enumerate([('Accepted 012 profile',A/'profile.png'),('Candidate profile',O/'profile.png'),('Side',O/'side.png'),('Rear',O/'rear.png')]):
        draw.text((i*300+8,8),label,fill='white');sheet.paste(black(Image.open(p).convert('RGBA')).resize((300,900)),(i*300,25))
    sheet.save(D/'profile-inspection.png')
    selected=trials[-1]
    write(D/'checkpoint.json',dict(checkpoint='013',status='validated candidate; awaiting final visual inspection and synchronization',accepted_variant=selected['variant'],previous_checkpoint='012',
        model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood-reopened.png'),pigment_sha256=hashes['assets/king/materials/king-pigment-atlas-v6.png'],scores=selected['scores'],original_iou_percent=selected['original_iou_percent'],equal_weight_mean=selected['equal_weight_mean'],holistic_visual_range_percent=[75,85],geometry_changed=True,material_changed=False,camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=9,modified_profile_rows=scope['modified_profile_rows'],edited_lights=scope['edited_lights'],mission_complete=False,validation=dict(scope='passed',receiver_regeneration='passed',export='passed',reproduction=checks,site='pending')))
    print('KING013_EVIDENCE_READY')

if __name__=='__main__':main()
