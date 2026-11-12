"""Archive rejected upper-base studies without replacing accepted assets."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import black,mask
from measure_base_reference import components

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    D=ROOT/'docs/king-mission/iteration-015';D.mkdir(parents=True,exist_ok=True)
    old=ROOT/'docs/king-mission/iteration-014';accepted=read(old/'checkpoint.json')
    source_hashes=read(old/'source-hashes.json')
    assert all(sha(ROOT/p)==v for p,v in source_hashes.items())
    write(D/'source-hashes.json',source_hashes)
    archived=read(ROOT/'history/king-mission-014/archive-manifest.json')
    for name,digest in archived.items():
        assert sha(ROOT/'history/king-mission-014'/name)==digest
        current=ROOT/('models/king/king-rebuilt.blend' if name=='king-rebuilt.blend' else 'assets/king/'+name)
        assert sha(current)==digest
    write(D/'accepted-preservation.json',dict(accepted_checkpoint='014',archive_and_current_exact=archived,source_hashes_exact=True))
    definitions=[
        ('165-upper-beam-aperture',80,68,'A wider beam adds an unwanted lower stripe instead of filling the upper patch.'),
        ('166-upper-source-width',80,68,'The larger emitter does not remove the doubled bands.'),
        ('167-upper-source-aim',80,67,'Re-aiming at the desired patch makes the lower streak more conspicuous.'),
        ('169-upper-coat-roughness',80,69,'Clear-coat roughness alone gives negligible useful change.'),
        ('170-upper-coat-and-beam',79,67,'Combined coat and broader beam produce a bright, low band.'),
        ('171-upper-shaped-reflections',80,69,'Three smaller sources enlarge the shine, but its dominant patch is too low and separated.'),
        ('172-upper-shaped-fitted',80,68,'Fitting prefers a narrow upper band and almost removes the third source; the desired continuous patch is still absent.'),
        ('173-upper-paired-reflections',80,68,'A broader pair is a diagnostic intermediate, with split highlights and insufficient match.'),
        ('174-upper-pair-fitted',80,68,'Fitting the broader pair retains two flat bright bands.'),
        ('175-upper-two-layer-finish',79,67,'Roughening both layers spreads the lower band and softens useful grain contrast.'),
        ('176-upper-finish-fitted',79,69,'The final fit softens the bands but does not recover the reference patch; no clear overall improvement over 014.')]
    reference=Image.open(ROOT/'assets/king/reference.png').convert('RGBA')
    baseline=Image.open(ROOT/'assets/king/render.png').convert('RGBA')
    target=np.asarray(black(reference),float);prior=np.asarray(black(baseline),float)
    foreground=mask(reference,True)&mask(baseline)
    regions={'upper-base':[510,815,635,920],'lower-base':[550,920,670,1000],'base-foot':[195,800,805,1110],'socket':[340,690,670,815],'collars':[300,390,715,565],'head':[310,0,705,350]}
    rows=[];measurements={}
    for name,grain,lighting,reason in definitions:
        T=ROOT/'build/king-mission'/name;E=D/'trials'/name;E.mkdir(parents=True,exist_ok=True)
        render=T/'wood-reopened.png';entry='canonical saved-file render'
        if not render.exists():render=T/'wood.png';entry='initial trial render; rejected intermediate, not independently reproduced'
        metrics=read(T/'metrics.json');assert metrics['render_sha256']==sha(render)
        scores=dict(silhouette_iou_percent=100*metrics['highres_iou'],interior_form=85,wood_color=82,grain_surface=grain,lighting_reflections=lighting)
        rows.append(dict(variant=name,decision='rejected',reason=reason,scores=scores,equal_weight_mean=sum(scores.values())/5,original_iou_percent=100*metrics['original_iou'],model_sha256=sha(T/'king.blend'),render_sha256=sha(render),render_entrypoint=entry))
        shutil.copy2(render,E/'wood.png')
        for file in ['input.json','parameters.json','metrics.json','base-comparison.png','fit.json','reflection-probes.json']:
            if (T/file).exists():shutil.copy2(T/file,E/file)
        actual=np.asarray(black(Image.open(render).convert('RGBA')),float);measurements[name]={}
        for region,(x0,y0,x1,y1) in regions.items():
            use=foreground[y0:y1,x0:x1];a=actual[y0:y1,x0:x1][use];p=prior[y0:y1,x0:x1][use];r=target[y0:y1,x0:x1][use]
            measurements[name][region]=dict(bounds=regions[region],foreground_pixels=int(use.sum()),baseline_rgb_mse=float(np.square(p-r).mean()),trial_rgb_mse=float(np.square(a-r).mean()),maximum_change_255=float(abs(a-p).max()),mean_change_255=float(abs(a-p).mean()))
        bright=(actual[:,:,2]>65)&(actual[:,:,1]>85)&(np.asarray(baseline)[:,:,3]>127);area=np.zeros(bright.shape,bool);area[790:1015,500:670]=True
        measurements[name]['bright_components']=components(bright&area)
    write(D/'scores.json',dict(accepted_checkpoint='014',accepted_scores=accepted['scores'],accepted_equal_weight_mean=accepted['equal_weight_mean'],holistic_visual_range_percent=[75,85],rubric='Only silhouette IoU is measured. Other percentages are subjective; fitting loss and effort do not earn acceptance.',trials=rows))
    write(D/'regional-measurements.json',dict(method='Fixed common foreground RGB error and thresholded bright components are diagnostics, not perceptual-match percentages. Reference pixels and registration unchanged.',trials=measurements))
    G=D/'diagnostics';G.mkdir(exist_ok=True)
    for source,prefix in [('164-base-response-diagnostic','base-'),('168-base-actual-surface','surface-')]:
        for p in (ROOT/'build/king-mission'/source).iterdir():
            if p.suffix in ('.json','.png'):shutil.copy2(p,G/(prefix+p.name))
    for name in ['full-comparison.png','socket-comparison.png','base-comparison.png','head-comparison.png','collars-comparison.png','overlay-highres.png','overlay-original.png']:
        shutil.copy2(ROOT/'build/king-mission/176-upper-finish-fitted'/name,D/('rejected-final-'+name))
    write(D/'checkpoint.json',dict(study='015',status='closed; all trial models rejected; owner requested pause',accepted_checkpoint='014',accepted_model_sha256=accepted['model_sha256'],accepted_render_sha256=accepted['render_sha256'],accepted_scores=accepted['scores'],accepted_equal_weight_mean=accepted['equal_weight_mean'],original_iou_percent=accepted['original_iou_percent'],camera_elevation_degrees=accepted['camera_elevation_degrees'],mission_complete=False,new_model_promoted=False,rejected_variants=[r['variant'] for r in rows]))
    print('KING015_REJECTED_STUDY_RECORDED',len(rows),flush=True)

if __name__=='__main__':main()
