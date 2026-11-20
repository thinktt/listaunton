"""Record checkpoint 012 with source preservation, reproduction and trial evidence."""
from pathlib import Path
import contextlib,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import audit,black,mask,iou
from record_seam_checkpoint import sha,read,write,rgba
from record_socket_checkpoint import original_colors_contact

def difference(a,b):
    a,b=rgba(a),rgba(b)
    return dict(maximum_channel_error_255=int(abs(a-b).max()),mean_channel_error_255=float(abs(a-b).mean()),alpha_exact=bool(np.array_equal(a[:,:,3],b[:,:,3])))

def main():
    D=ROOT/'docs/king-mission/iteration-012';O=ROOT/'build/king-mission/135-middle-collar-clean-join'
    P=ROOT/'build/king-mission/136-collar-turning-reproduction';A=ROOT/'history/king-mission-011'
    original=D/'render-before-reopen.png'
    if not original.exists():shutil.copy2(O/'wood.png',original)
    canonical=ROOT/'build/king-mission/140-standardized-fresh-render/wood-reopened.png'
    repeated=ROOT/'build/king-mission/141-standardized-repeat/wood-reopened.png'
    session=difference(original,canonical);fresh=difference(canonical,P/'wood-reopened.png');repeat=difference(canonical,repeated)
    assert fresh['maximum_channel_error_255']<=1 and fresh['alpha_exact'],fresh
    assert repeat['maximum_channel_error_255']<=1 and repeat['alpha_exact'],repeat
    checks=dict(initial_session_vs_fresh=session,independent_saved_reproduction=fresh,repeat_saved_render=repeat,
        alternate_entrypoint=difference(canonical,O/'wood-reopened.png'),
        canonical_render_entrypoint='scripts/king/render_fixed_diagnostics.py -- SOURCE OUTPUT --beauty-only',
        remaining_limitation='A different rendering entry point changes a tiny socket glint. Fixed samples and removing denoising did not resolve it. Scene data agree; precise execution-context cause remains unresolved. The failed checks are retained, not relabeled as passes.',
        reproduction_mesh_exact=sha(O/'mesh.bin')==sha(P/'mesh.bin'),camera_export_exact=sha(O/'camera.json')==sha(A/'camera.json'),
        physical_bounds_exact=read(O/'mesh.json')['bounds']==read(A/'mesh.json')['bounds'])
    assert all(checks[k] for k in ['reproduction_mesh_exact','camera_export_exact','physical_bounds_exact'])
    write(D/'reproduction-checks.json',checks);shutil.copy2(O/'wood-reopened.png',D/'alternate-entrypoint-render.png');shutil.copy2(canonical,O/'wood.png')
    hashes=read(ROOT/'docs/king-mission/iteration-011/source-hashes.json')
    assert all(sha(ROOT/k)==v for k,v in hashes.items());write(D/'source-hashes.json',hashes)
    write(A/'archive-manifest.json',{p.name:sha(p) for p in A.iterdir() if p.is_file() and p.name!='archive-manifest.json'})
    definitions=[
        ('128-collar-unlit-blend',84,79,77,65,'rejected','Broad inferred wood blend is too orange and softens the source grain.'),
        ('129-collar-neutral-residual',84,81,79,66,'rejected','Neutral-component pigment removal darkens the wood without improving the overall collar match.'),
        ('130-rounded-middle-collar',85,82,79,66,'superseded','Curvature clears the previously obstructed glint path; later checks find a retained baseline join crossing.'),
        ('131-middle-collar-fitted',85,82,79,66,'rejected','Power fit produces an overly thin bright stripe; baseline join crossing remains.'),
        ('132-middle-broad-glint',85,82,79,66,'superseded','Broader reflector still aims too far left; baseline join crossing remains.'),
        ('133-middle-centered-glints',85,82,79,67,'superseded','Better placement, but the existing collar join crossing must be repaired.'),
        ('134-centered-glints-fitted',85,82,79,66,'rejected','Automated fitting over-brightens the inner groove; baseline join crossing remains.'),
        ('135-middle-collar-clean-join',85,82,79,67,'validated candidate','Continuous join, gentler centered glints and a rounder middle edge. Standardized fresh rendering repeats and agrees with an independent rebuild; alternate-entry-point glint variation remains documented.'),
        ('137-clean-collar-fixed-sampling',85,82,79,67,'rejected','Fixed 256 samples do not resolve the tiny alternate-entry-point socket discrepancy; no worthwhile visible improvement.')]
    trials=[]
    for variant,interior,color,grain,lighting,decision,reason in definitions:
        T=ROOT/'build/king-mission'/variant
        with (T/'audit.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log):audit(T/'wood.png',A/'render.png',T,T/'king.blend')
        m=read(T/'metrics.json');scores=dict(silhouette_iou_percent=m['highres_iou']*100,interior_form=interior,wood_color=color,grain_surface=grain,lighting_reflections=lighting)
        trials.append(dict(variant=variant,decision=decision,reason=reason,scores=scores,original_iou_percent=m['original_iou']*100,equal_weight_mean=sum(scores.values())/5,model_sha256=sha(T/'king.blend'),render_sha256=sha(T/'wood.png')))
        E=D/'trials'/variant;E.mkdir(parents=True,exist_ok=True)
        for name in ['parameters.json','wood.png','fit.json','repair.json','turning.json','metrics.json']:
            if (T/name).exists():shutil.copy2(T/name,E/name)
        print(variant,scores,flush=True)
    write(D/'scores.json',dict(rubric='Only silhouette IoU is measured; all other ratings are visual judgments using the unchanged rubric.',holistic_visual_range_percent=[75,85],trials=trials))
    actual=rgba(O/'wood.png');ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');rm=mask(ref,True)
    target=np.asarray(black(ref),dtype=float);old=np.asarray(black(Image.open(A/'render.png').convert('RGBA')),dtype=float);new=np.asarray(black(Image.open(O/'wood.png').convert('RGBA')),dtype=float)
    common=(actual[:,:,3]>127)&rm;regions={}
    for name,box in [('head',[185,0,815,350]),('collars',[300,390,710,555]),('middle-collar',[370,445,650,510]),('stem',[185,560,815,720]),('socket',[370,720,630,810]),('base-foot',[185,840,815,1110])]:
        x0,y0,x1,y1=box;m=common[y0:y1,x0:x1];a=old[y0:y1,x0:x1][m];b=new[y0:y1,x0:x1][m];t=target[y0:y1,x0:x1][m]
        regions[name]=dict(bounds=box,foreground_pixels=int(m.sum()),previous_rgb_mse=float(np.square(a-t).mean()),trial_rgb_mse=float(np.square(b-t).mean()),maximum_render_change_255=float(abs(a-b).max()),mean_render_change_255=float(abs(a-b).mean()))
    write(D/'regional-measurements.json',dict(method='Composited foreground RGB squared error in fixed rectangles; not a perceptual match percentage.',regions=regions))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','parameters.json','turning.json','neutral.png','profile.png','rear.png','side.png']:shutil.copy2(O/name,D/name)
    diag=D/'diagnostic-127';diag.mkdir(exist_ok=True)
    for p in (ROOT/'build/king-mission/127-collar-finish-diagnostic').iterdir():
        if p.suffix in ['.json','.png']:shutil.copy2(p,diag/p.name)
    original_colors_contact(D,O)
    canvas=Image.new('RGB',(1200,925),'#17191b');draw=ImageDraw.Draw(canvas)
    for i,(label,path) in enumerate([('Previous profile',A/'profile.png'),('Revised profile',O/'profile.png'),('Side',O/'side.png'),('Rear',O/'rear.png')]):
        draw.text((i*300+8,8),label,fill='white');im=black(Image.open(path).convert('RGBA')).resize((300,900));canvas.paste(im,(i*300,25))
    canvas.save(D/'profile-inspection.png')
    selected=next(row for row in trials if row['variant']==O.name);scope=read(D/'scope-check.json')
    write(D/'checkpoint.json',dict(checkpoint='012',status='validated candidate; awaiting visual acceptance and page synchronization',accepted_variant=selected['variant'],previous_checkpoint='011',model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood.png'),pigment_sha256=hashes['assets/king/materials/king-pigment-atlas-v6.png'],scores=selected['scores'],original_iou_percent=selected['original_iou_percent'],equal_weight_mean=selected['equal_weight_mean'],holistic_visual_range_percent=[75,85],geometry_changed=True,material_changed=False,camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=9,modified_profile_rows=scope['modified_profile_rows'],edited_lights=scope['edited_lights'],mission_complete=False,validation=dict(scope='passed',receiver_regeneration='passed',export='passed',reproduction=checks,site='pending')))
    print('KING012_EVIDENCE_READY',flush=True)

if __name__=='__main__':main()
