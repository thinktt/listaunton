"""Record the king collar study, rejected hypotheses and validated checkpoint."""
from pathlib import Path
import json,shutil,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import mask,iou,black
from record_seam_checkpoint import sha,read,write,rgba
from record_socket_checkpoint import original_colors_contact

def main():
    D=ROOT/'docs/king-mission/iteration-011';O=ROOT/'build/king-mission/117-collar-fitted-reflections'
    P=ROOT/'build/king-mission/126-collar-checkpoint-reproduction';A=ROOT/'history/king-mission-010'
    actual=rgba(O/'wood.png');checks={}
    for name,path in [('saved_reopened',O/'wood-reopened.png'),('full_reproduction',P/'wood.png')]:
        test=rgba(path);row=dict(maximum_channel_error_255=int(abs(test-actual).max()),mean_channel_error_255=float(abs(test-actual).mean()),alpha_exact=bool(np.array_equal(test[:,:,3],actual[:,:,3])))
        assert row['maximum_channel_error_255']<=1 and row['alpha_exact'],(name,row);checks[name]=row
    checks.update(reproduction_mesh_exact=sha(O/'mesh.bin')==sha(P/'mesh.bin'),
        accepted_geometry_export_byte_identical_to_010=sha(O/'mesh.bin')==sha(A/'mesh.bin'),
        camera_export_byte_identical_to_010=sha(O/'camera.json')==sha(A/'camera.json'),
        physical_bounds_exact=read(O/'mesh.json')['bounds']==read(A/'mesh.json')['bounds'])
    assert all(checks[k] for k in ['reproduction_mesh_exact','accepted_geometry_export_byte_identical_to_010','camera_export_byte_identical_to_010','physical_bounds_exact'])
    initial=read(D/'partition-render-diagnostic.json');diag=read(ROOT/'build/king-mission/120-collar-partition-diagnostic/diagnostic.json')
    assert initial['alpha_exact'] and all(r['byte_exact'] for r in diag['unchanged_receiver_normals'].values())
    assert all(r['max_linear_error']<3e-6 and r['alpha_exact'] for r in diag['render_differences'].values())
    checks['partition_preservation']=dict(initial_full_render=initial,initial_one_level_check_passed=False,
        fixed_sample_diagnostic=diag,interpretation='The initial 128-sample adaptive/denoised render failed the 1/255 maximum check. The unchanged receiver normals are byte-identical and fixed 1024-sample undenoised comparisons agree to 2.15e-6 linear. This supports sampling/denoising sensitivity; the failed initial check is retained, not relabeled as a pass.')
    write(D/'reproduction-checks.json',checks);print('Reproduction checks pass; partition diagnostic retained.',flush=True)
    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');rm=mask(ref,True);target=np.asarray(black(ref),dtype=float)
    reg=read(ROOT/'assets/king/original-alignment.json');scale,x,y=(reg[k] for k in ('scale','x','y'));W=ref.width
    original=Image.open(ROOT/'assets/king/original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(scale*300/W,0,x*3,0,scale*300/W,y*3),Image.Resampling.BILINEAR);om=mask(original,True)
    definitions=[
      ('115-collar-local-reflections',64,'superseded','Broad striping is reduced, but unfitted sources are weak and one is obstructed.'),
      ('116-collar-partition-baseline',64,'diagnostic','Illumination-preservation render; no improvement claimed.'),
      ('117-collar-fitted-reflections',66,'proposed acceptance after checks','Warmer separated lower glints and reduced repeated pale bands; missing upper/middle glints remain.'),
      ('118-collar-near-reflections',64,'rejected','Near emitters do not recover broad natural crescents.'),
      ('119-collar-near-fitted',65,'rejected','A bright isolated middle-collar dot is less faithful than the simpler trial.'),
      ('122-collar-textured-normals',64,'rejected','Measured-normal aiming still leaves an unsuitable near-field highlight.'),
      ('123-collar-textured-fitted',65,'rejected','Lower fitting loss does not outweigh the bright dot and poorer full-render regional match.'),
      ('124-collar-middle-shadow-study',65,'rejected','Single-light shadow omission gives no worthwhile visible benefit.'),
      ('125-collar-middle-fitted',66,'not accepted','Almost the same visible result as 117; the added shadow approximation is unjustified.')]
    trials=[]
    for variant,lighting,decision,reason in definitions:
        p=ROOT/'build/king-mission'/variant;im=Image.open(p/'wood.png').convert('RGBA');mm=mask(im);a=np.asarray(black(im),dtype=float)
        scores=dict(silhouette_iou_percent=iou(rm,mm)*100,interior_form=84,wood_color=82,grain_surface=79,lighting_reflections=lighting)
        regional={name:float(np.square(a[y0:y1,x0:x1]-target[y0:y1,x0:x1]).mean()) for name,(x0,y0,x1,y1) in [('upper',(390,395,610,445)),('middle',(370,445,650,505)),('lower',(360,505,660,550))]}
        trials.append(dict(variant=variant,decision=decision,reason=reason,scores=scores,original_iou_percent=iou(om,mm)*100,
            equal_weight_mean=sum(scores.values())/5,regional_rgb_mse=regional,render_sha256=sha(p/'wood.png'),model_sha256=sha(p/'king.blend')))
        E=D/'trials'/variant;E.mkdir(parents=True,exist_ok=True)
        for name in ['parameters.json','wood.png','fit.json']:
            if (p/name).exists():shutil.copy2(p/name,E/name)
        print(variant,scores,flush=True)
    write(D/'scores.json',dict(rubric='Only IoU is measured; other scores are visual judgments using the unchanged rubric. Emission and partition diagnostics are not accepted beauty renders.',trials=trials,holistic_visual_range_percent=[75,84]))
    old=np.asarray(black(Image.open(A/'render.png').convert('RGBA')),dtype=float);new=np.asarray(black(Image.open(O/'wood.png').convert('RGBA')),dtype=float);common=(actual[:,:,3]>127)&rm;regions={}
    for name,box in [('head',[185,0,815,350]),('collars',[300,390,710,555]),('stem',[185,560,815,720]),('socket',[370,720,630,810]),('base-foot',[185,840,815,1110])]:
        x0,y0,x1,y1=box;m=common[y0:y1,x0:x1];a=old[y0:y1,x0:x1][m];b=new[y0:y1,x0:x1][m];t=target[y0:y1,x0:x1][m]
        regions[name]=dict(bounds=box,foreground_pixels=int(m.sum()),previous_rgb_mse=float(np.square(a-t).mean()),trial_rgb_mse=float(np.square(b-t).mean()),maximum_render_change_255=float(abs(a-b).max()),mean_render_change_255=float(abs(a-b).mean()))
    write(D/'regional-measurements.json',dict(method='Composited RGB error in fixed rectangles, excluding background; not a perceptual match percentage.',regions=regions))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','fit.json','parameters.json','fixed-response.exr','neutral.png','profile.png','rear.png','side.png']+[f'response-{i:02}.exr' for i in range(6)]:shutil.copy2(O/name,D/name)
    for variant in ['120-collar-partition-diagnostic','121-collar-surface']:
        E=D/variant;E.mkdir(exist_ok=True)
        for p in (ROOT/'build/king-mission'/variant).iterdir():
            if p.is_file():shutil.copy2(p,E/p.name)
    shutil.copy2(O/'response-diagnostic.json',D/'117-response-diagnostic.json')
    original_colors_contact(D,O)
    selected=next(r for r in trials if r['variant']=='117-collar-fitted-reflections')
    write(D/'checkpoint.json',dict(checkpoint='011',status='candidate validated; pending visual acceptance and review synchronization',accepted_variant=selected['variant'],previous_checkpoint='010',
        model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood.png'),pigment_sha256=sha(ROOT/'assets/king/materials/king-pigment-atlas-v6.png'),
        scores=selected['scores'],original_iou_percent=selected['original_iou_percent'],equal_weight_mean=selected['equal_weight_mean'],holistic_visual_range_percent=[75,84],
        geometry_changed=False,material_changed=False,camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=9,
        added_lights=read(D/'scope-check.json')['added_lights'],mission_complete=False,
        validation=dict(reproduction=checks,scope='passed',receiver_regeneration='passed',export='passed',site='pending')))
    print('KING011_EVIDENCE_READY',flush=True)

if __name__=='__main__':main()
