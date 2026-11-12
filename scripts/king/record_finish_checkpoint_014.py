"""Record the scoped collar-finish study; does not replace the current king."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import black,mask
from record_socket_checkpoint import original_colors_contact
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    D=ROOT/'docs/king-mission/iteration-014';A=ROOT/'history/king-mission-013';O=ROOT/'build/king-mission/162-no-tree-collar'
    checks=read(D/'reproduction-checks.json');scope=read(D/'scope-check.json')
    for key in ('independent_saved_reproduction','repeat_saved_render'):
        assert checks[key]['maximum_channel_error_255']<=1 and checks[key]['alpha_exact']
    assert all(checks[k] for k in ('baseline_mesh_exact','reproduction_mesh_exact','camera_export_exact','physical_bounds_exact'))
    if not (D/'render-before-reopen.png').exists():shutil.copy2(O/'wood.png',D/'render-before-reopen.png')
    shutil.copy2(O/'wood-reopened.png',O/'wood.png')
    hashes=read(ROOT/'docs/king-mission/iteration-013/source-hashes.json')
    assert all(sha(ROOT/p)==v for p,v in hashes.items());write(D/'source-hashes.json',hashes)
    assert sha(A/'king-rebuilt.blend')=='5f0671fa5484a1e52a75b3d93a4e9d93538b1294e4f33db44e68de1199a2398d'
    definitions=[
        ('153-collar-neutral-chroma',79,69,'rejected','Chroma-only repair has negligible visible benefit and does not remove the pale bands.'),
        ('155-collar-measured-pigment',79,69,'rejected','Current-light inverse pigment changes little; the remaining streaks are substantially reflections. Its legacy helper also mislabeled the prepared-scene hash as the original source hash; no prototype asset is promoted.'),
        ('157-collar-grain-relief',80,69,'superseded; repetition check failed','Moderate relief improves collar highlights, but a repeated saved-file render differs by 45/255 at a small socket glint. Failed checks are retained; this version is not promoted.'),
        ('158-collar-soft-grain',80,68,'rejected','Extra coat roughness softens useful contrast without clearly improving the match beyond the medium relief trial.'),
        ('159-collar-deeper-grain',78,68,'rejected','Stronger relief makes the collar surface too dotted and uneven.'),
        ('161-no-tree-baseline',79,69,'sampling diagnostic','Unchanged checkpoint-013 geometry and material with light-tree sampling disabled; no appearance score gain is assigned for sampling alone.'),
        ('162-no-tree-collar',80,69,'validated candidate','Moderate collar varnish relief with light-tree sampling disabled. Grain is less smooth; pale bands and exact highlight positions remain unresolved.')]
    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');prior=Image.open(A/'render.png').convert('RGBA')
    target=np.asarray(black(ref),dtype=float);old=np.asarray(black(prior),dtype=float);common=mask(ref,True)&mask(prior)
    regions={'collars':[300,390,710,555],'upper-collar':[370,400,650,453],'middle-collar':[325,448,690,505],'lower-collar':[305,495,710,555],'head':[185,0,815,350],'socket':[340,690,670,845],'base-foot':[195,840,805,1110]}
    trials=[];measurements={}
    for name,grain,lighting,decision,reason in definitions:
        T=ROOT/'build/king-mission'/name;E=D/'trials'/name;E.mkdir(parents=True,exist_ok=True);m=read(T/'metrics.json')
        scores=dict(silhouette_iou_percent=m['highres_iou']*100,interior_form=85,wood_color=82,grain_surface=grain,lighting_reflections=lighting)
        trials.append(dict(variant=name,scores=scores,equal_weight_mean=sum(scores.values())/5,original_iou_percent=m['original_iou']*100,decision=decision,reason=reason,model_sha256=sha(T/'king.blend'),render_sha256=sha(T/'wood-reopened.png')))
        for src,dst in [('wood-reopened.png','wood.png'),('metrics.json','metrics.json'),('parameters.json','parameters.json'),('collars-comparison.png','collars-comparison.png')]:shutil.copy2(T/src,E/dst)
        cfg=read(T/'input.json');cfg['source']='history/king-mission-013/king-rebuilt.blend';write(E/'input.json',cfg)
        actual=np.asarray(black(Image.open(T/'wood-reopened.png').convert('RGBA')),dtype=float);measurements[name]={}
        for region,(x0,y0,x1,y1) in regions.items():
            use=common[y0:y1,x0:x1];a=actual[y0:y1,x0:x1][use];b=old[y0:y1,x0:x1][use];r=target[y0:y1,x0:x1][use]
            measurements[name][region]=dict(bounds=regions[region],foreground_pixels=int(use.sum()),previous_rgb_mse=float(np.square(b-r).mean()),trial_rgb_mse=float(np.square(a-r).mean()),maximum_render_change_255=float(abs(a-b).max()),mean_render_change_255=float(abs(a-b).mean()))
    write(D/'scores.json',dict(rubric='Only silhouette IoU is measured. Other values are subjective visual assessments; a small grain improvement does not resolve the visible lighting and form mismatches.',holistic_visual_range_percent=[75,85],trials=trials))
    write(D/'regional-measurements.json',dict(method='Composited RGB squared error on common fixed foreground. This is not a perceptual-match percentage; no background pixels are counted.',trials=measurements))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','neutral.png','profile.png','rear.png','side.png']:shutil.copy2(O/name,D/name)
    G=D/'diagnostics';G.mkdir(exist_ok=True)
    for p in (ROOT/'build/king-mission/156-collar-finish-diagnosis').iterdir():
        if p.suffix in ('.json','.png'):shutil.copy2(p,G/p.name)
    shutil.copy2(ROOT/'build/king-mission/154-collar-pigment-response/response.json',G/'response.json')
    original_colors_contact(D,O)
    sheet=Image.new('RGB',(1200,925),'#17191b');draw=ImageDraw.Draw(sheet)
    for i,(label,path) in enumerate([('Accepted 013 profile',A/'profile.png'),('Candidate profile',O/'profile.png'),('Side',O/'side.png'),('Rear',O/'rear.png')]):
        draw.text((i*300+8,8),label,fill='white');sheet.paste(black(Image.open(path).convert('RGBA')).resize((300,900)),(i*300,25))
    sheet.save(D/'profile-inspection.png')
    selected=next(t for t in trials if t['variant']=='162-no-tree-collar')
    write(D/'checkpoint.json',dict(checkpoint='014',status='validated candidate; awaiting final visual inspection and synchronization',accepted_variant=selected['variant'],previous_checkpoint='013',model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood-reopened.png'),pigment_sha256=hashes['assets/king/materials/king-pigment-atlas-v6.png'],scores=selected['scores'],original_iou_percent=selected['original_iou_percent'],equal_weight_mean=selected['equal_weight_mean'],holistic_visual_range_percent=[75,85],geometry_changed=False,material_changed=True,lights_changed=False,declared_finish=scope['declared_finish'],camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=9,mission_complete=False,validation=dict(scope='passed',receiver_regeneration='passed',export='passed',reproduction=checks,site='pending')))
    print('KING014_EVIDENCE_READY',flush=True)

if __name__=='__main__':main()
