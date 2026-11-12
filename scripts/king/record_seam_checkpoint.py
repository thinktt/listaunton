"""Record the king inner-seam study and its reproducible accepted result."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import mask,iou,black
from record_socket_checkpoint import original_colors_contact

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def rgba(p):return np.asarray(Image.open(p).convert('RGBA'),dtype=np.int16)


def main():
    D=ROOT/'docs/king-mission/iteration-010';O=ROOT/'build/king-mission/113-socket-fitted-seam';P=ROOT/'build/king-mission/114-seam-checkpoint-reproduction';A=ROOT/'history/king-mission-009'
    actual=rgba(O/'wood.png');previous=rgba(A/'render.png');checks={}
    for name,path in [('saved_reopened',O/'wood-reopened.png'),('full_reproduction',P/'wood.png')]:
        test=rgba(path);row=dict(maximum_channel_error_255=int(abs(test-actual).max()),mean_channel_error_255=float(abs(test-actual).mean()),alpha_exact=bool(np.array_equal(test[:,:,3],actual[:,:,3])))
        assert row['maximum_channel_error_255']<=1 and row['alpha_exact'],(name,row)
        checks[name]=row
    checks['reproduction_mesh_exact']=sha(O/'mesh.bin')==sha(P/'mesh.bin')
    checks['accepted_geometry_export_byte_identical_to_009']=sha(O/'mesh.bin')==sha(A/'mesh.bin')
    checks['camera_export_byte_identical_to_009']=sha(O/'camera.json')==sha(A/'camera.json')
    checks['physical_bounds_exact']=read(O/'mesh.json')['bounds']==read(A/'mesh.json')['bounds']
    assert all(checks[n] for n in ['reproduction_mesh_exact','accepted_geometry_export_byte_identical_to_009','camera_export_byte_identical_to_009','physical_bounds_exact'])
    baseline=rgba(ROOT/'build/king-mission/112-seam-partition-baseline/wood.png')
    checks['preserving_seam_split']=dict(maximum_channel_error_255=int(abs(baseline-previous).max()),alpha_exact=bool(np.array_equal(baseline[:,:,3],previous[:,:,3])))
    assert checks['preserving_seam_split']['maximum_channel_error_255']<=1 and checks['preserving_seam_split']['alpha_exact']
    write(D/'reproduction-checks.json',checks);print('Reproduction and exact geometry/camera checks pass.',flush=True)

    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');refmask=mask(ref,True);target=np.asarray(black(ref),dtype=float)
    reg=read(ROOT/'assets/king/original-alignment.json');scale,x,y=(reg[k] for k in ('scale','x','y'));W=ref.width
    original=Image.open(ROOT/'assets/king/original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(scale*300/W,0,x*3,0,scale*300/W,y*3),Image.Resampling.BILINEAR);omask=mask(original,True)
    rows=[
        ('106-socket-pigment-center',81,63,'rejected','Broad manual grade changes neighboring colors that were already close.'),
        ('107-socket-fitted-pigment',82,63,'not accepted','Non-highlight fit favors a mild lift; insufficient clear visual improvement to replace the finish.'),
        ('108-socket-narrow-pigment',82,63,'deferred','Central patch error improves, but this is not a complete socket-color correction; preserve for focused follow-up.'),
        ('109-socket-inner-seam-area',82,58,'rejected','Unconfined lights create broad bright patches on the neighboring stem.'),
        ('110-socket-polished-seam',82,62,'rejected','Local polish gives a fine line but does not remove adjacent stem spill.'),
        ('111-socket-seam-receiver',82,64,'superseded','Exact fillet receiver confines the glints without changing the accepted material.'),
        ('112-seam-partition-baseline',82,63,'diagnostic','Partition-only preservation render; no improvement claimed.'),
        ('113-socket-fitted-seam',82,64,'proposed acceptance after checks','Fitted real reflections improve the inner line while retaining the outer glints, color, grain and geometry.')]
    trials=[]
    for variant,color,lighting,decision,reason in rows:
        p=ROOT/'build/king-mission'/variant;im=Image.open(p/'wood.png').convert('RGBA');m=mask(im);a=np.asarray(black(im),dtype=float)
        scores=dict(silhouette_iou_percent=iou(refmask,m)*100,interior_form=84,wood_color=color,grain_surface=79,lighting_reflections=lighting)
        regional={label:float(np.square(a[y0:y1,x0:x1]-target[y0:y1,x0:x1]).mean()) for label,(x0,y0,x1,y1) in [('socket',(370,720,630,810)),('quiet_center',(485,760,520,783)),('inner_seam',(425,730,590,758))]}
        trials.append(dict(variant=variant,decision=decision,reason=reason,scores=scores,original_iou_percent=iou(omask,m)*100,equal_weight_mean=sum(scores.values())/5,
                           render_sha256=sha(p/'wood.png'),model_sha256=sha(p/'king.blend'),regional_rgb_mse=regional))
        E=D/'trials'/variant;E.mkdir(parents=True,exist_ok=True)
        for name in ['parameters.json','wood.png']:shutil.copy2(p/name,E/name)
        if (p/'fit.json').exists():shutil.copy2(p/'fit.json',E/'fit.json')
        print(variant,scores,flush=True)
    write(D/'scores.json',dict(rubric='IoU alone is measured; other ratings are visual judgments. Tiny alpha-threshold variation is not shape improvement. Diagnostic emission/diffuse crops are not final render candidates.',trials=trials,holistic_visual_range_percent=[74,83]))
    common=(actual[:,:,3]>127)&refmask;oldrgb=np.asarray(black(Image.open(A/'render.png').convert('RGBA')),dtype=float);newrgb=np.asarray(black(Image.open(O/'wood.png').convert('RGBA')),dtype=float);regions={}
    for name,box in [('head',[185,0,815,350]),('collars',[185,350,815,560]),('stem',[185,560,815,720]),('socket',[370,720,630,810]),('inner-seam',[425,730,590,758]),('quiet-center',[485,760,520,783]),('base-foot',[185,840,815,1110])]:
        x0,y0,x1,y1=box;m=common[y0:y1,x0:x1];old=oldrgb[y0:y1,x0:x1][m];new=newrgb[y0:y1,x0:x1][m];t=target[y0:y1,x0:x1][m]
        regions[name]=dict(bounds=box,foreground_pixels=int(m.sum()),previous_rgb_mse=float(np.square(old-t).mean()),trial_rgb_mse=float(np.square(new-t).mean()),maximum_render_change_255=float(abs(old-new).max()),mean_render_change_255=float(abs(old-new).mean()))
    write(D/'regional-measurements.json',dict(method='Composited RGB error in fixed rectangles, excluding background. Not a perceptual match percentage.',regions=regions))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','fit.json','parameters.json','fixed-response.exr','response-00.exr','response-01.exr','neutral.png','profile.png','rear.png','side.png']:shutil.copy2(O/name,D/name)
    diagnostic=D/'105-diagnostic';diagnostic.mkdir(exist_ok=True)
    for p in (ROOT/'build/king-mission/105-socket-finish-diagnostic').iterdir():
        if p.is_file():shutil.copy2(p,diagnostic/p.name)
    original_colors_contact(D,O)
    write(D/'checkpoint.json',dict(checkpoint='010',status='candidate validated; pending visual acceptance and review synchronization',accepted_variant='113-socket-fitted-seam',previous_checkpoint='009',
        model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood.png'),pigment_sha256=sha(ROOT/'assets/king/materials/king-pigment-atlas-v6.png'),
        scores=trials[-1]['scores'],original_iou_percent=trials[-1]['original_iou_percent'],equal_weight_mean=trials[-1]['equal_weight_mean'],holistic_visual_range_percent=[74,83],
        geometry_changed=False,material_changed=False,camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=6,added_lights=read(D/'scope-check.json')['added_lights'],mission_complete=False,
        validation=dict(reproduction=checks,scope='passed',receiver_regeneration='passed',export='passed',site='pending')))
    print('KING010_EVIDENCE_READY',flush=True)


if __name__=='__main__':main()
