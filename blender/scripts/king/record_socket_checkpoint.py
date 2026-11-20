"""Record fixed-camera king socket trials, preservation and reproducibility."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from audit_mission import mask,iou,black


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def rgba(p):return np.asarray(Image.open(p).convert('RGBA'),dtype=np.int16)


def original_colors_contact(D,O):
    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');reg=read(ROOT/'assets/king/original-alignment.json')
    scale,x,y=(reg[k] for k in ('scale','x','y'));W=ref.width
    affine=(scale*300/W,0,x*3,0,scale*300/W,y*3)
    original=Image.open(ROOT/'assets/king/original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,affine,Image.Resampling.BILINEAR)
    white=Image.open(ROOT/'references/lichess-staunton-3d/White-King.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,affine,Image.Resampling.BILINEAR)
    canvas=Image.new('RGB',(840,530),'#17191b');draw=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate([('Original black',original),('Original white',white),('Current model',Image.open(O/'wood.png').convert('RGBA'))]):
        im=black(im.crop((185,0,815,1110))).resize((260,458),Image.Resampling.LANCZOS)
        canvas.paste(im,(i*280+10,52));draw.text((i*280+15,12),label,fill='white')
    canvas.save(D/'original-colors-inspection.png')


def main():
    D=ROOT/'docs/king-mission/iteration-009';O=ROOT/'build/king-mission/103-socket-fitted-glints';P=ROOT/'build/king-mission/104-socket-checkpoint-reproduction';A=ROOT/'history/king-mission-007'
    actual=rgba(O/'wood.png');previous=rgba(A/'render.png')
    checks={}
    for name,path in [('saved_reopened',O/'wood-reopened.png'),('full_reproduction',P/'wood.png')]:
        test=rgba(path);row=dict(maximum_channel_error_255=int(abs(test-actual).max()),mean_channel_error_255=float(abs(test-actual).mean()),alpha_exact=bool(np.array_equal(test[:,:,3],actual[:,:,3])))
        assert row['maximum_channel_error_255']<=1 and row['alpha_exact'],(name,row)
        checks[name]=row
    checks['reproduction_mesh_exact']=sha(O/'mesh.bin')==sha(P/'mesh.bin')
    checks['accepted_geometry_export_byte_identical_to_007']=sha(O/'mesh.bin')==sha(A/'mesh.bin')
    checks['camera_export_byte_identical_to_007']=sha(O/'camera.json')==sha(A/'camera.json')
    checks['physical_bounds_size_exact']=read(O/'mesh.json')['bounds']==read(A/'mesh.json')['bounds']
    assert all(checks[n] for n in ['reproduction_mesh_exact','accepted_geometry_export_byte_identical_to_007','camera_export_byte_identical_to_007','physical_bounds_size_exact'])
    baseline=rgba(ROOT/'build/king-mission/097-socket-partition-baseline/wood.png')
    checks['preserving_socket_split']=dict(maximum_channel_error_255=int(abs(baseline-previous).max()),alpha_exact=bool(np.array_equal(baseline[:,:,3],previous[:,:,3])))
    assert checks['preserving_socket_split']['maximum_channel_error_255']<=1 and checks['preserving_socket_split']['alpha_exact']
    write(D/'reproduction-checks.json',checks)
    print('Saved/reopened, independent reproduction, export and bounds checks pass.',flush=True)

    ref=Image.open(ROOT/'assets/king/reference.png').convert('RGBA');refmask=mask(ref,True);target=np.asarray(black(ref),dtype=float)
    reg=read(ROOT/'assets/king/original-alignment.json');scale,x,y=(reg[k] for k in ('scale','x','y'));W=ref.width
    original=Image.open(ROOT/'assets/king/original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(scale*300/W,0,x*3,0,scale*300/W,y*3),Image.Resampling.BILINEAR)
    omask=mask(original,True);trials=[]
    rows=[
        ('097-socket-partition-baseline',62,'diagnostic','Exact receiver migration; no visual improvement claimed.'),
        ('098-socket-separated-warm',61,'rejected','Area lights introduce duplicate reflections on the inner socket slope.'),
        ('099-socket-confined-spots',60,'rejected','Narrow distant spots leave the desired outer glints too weak, despite lower crop error.'),
        ('100-socket-small-sources',60,'rejected','Brighter small distant sources restore intrusive inner-slope glints.'),
        ('101-socket-local-sources',62,'superseded','Closer sources separate the glints, but their footprints are small and too bright.'),
        ('102-socket-shaped-glints',62,'superseded','Paired small sources give curved footprints; right glints remain too bright.'),
        ('103-socket-fitted-glints',63,'proposed acceptance after checks','Improved glint separation, warmth and brightness balance; the inner seam and patchy grain still differ.')]
    for variant,lighting,decision,reason in rows:
        p=ROOT/'build/king-mission'/variant;im=Image.open(p/'wood.png').convert('RGBA');m=mask(im)
        scores=dict(silhouette_iou_percent=iou(refmask,m)*100,interior_form=84,wood_color=82,grain_surface=79,lighting_reflections=lighting)
        a=np.asarray(black(im),dtype=float);bounds=[370,720,630,810];x0,y0,x1,y1=bounds
        row=dict(variant=variant,decision=decision,reason=reason,scores=scores,original_iou_percent=iou(omask,m)*100,
                 equal_weight_mean=sum(scores.values())/5,render_sha256=sha(p/'wood.png'),model_sha256=sha(p/'king.blend'),
                 socket_crop_rgb_mse=float(np.square(a[y0:y1,x0:x1]-target[y0:y1,x0:x1]).mean()))
        trials.append(row)
        E=D/'trials'/variant;E.mkdir(parents=True,exist_ok=True)
        for name in ['parameters.json','wood.png']:shutil.copy2(p/name,E/name)
        print(variant,row['scores'],flush=True)
    write(D/'scores.json',dict(rubric='Only silhouette IoU is measured. The other four scores are visual judgments; no gain is awarded for tiny sampling-related alpha differences on unchanged geometry.',trials=trials,holistic_visual_range_percent=[74,83]))

    common=(actual[:,:,3]>127)&refmask
    oldrgb=np.asarray(black(Image.open(A/'render.png').convert('RGBA')),dtype=float);newrgb=np.asarray(black(Image.open(O/'wood.png').convert('RGBA')),dtype=float)
    regions={}
    for name,box in [('head',[185,0,815,350]),('collars',[185,350,815,560]),('stem',[185,560,815,720]),('socket',[370,720,630,810]),('base-foot',[185,840,815,1110])]:
        x0,y0,x1,y1=box;m=common[y0:y1,x0:x1];old=oldrgb[y0:y1,x0:x1][m];new=newrgb[y0:y1,x0:x1][m];t=target[y0:y1,x0:x1][m]
        regions[name]=dict(bounds=box,foreground_pixels=int(m.sum()),previous_rgb_mse=float(np.square(old-t).mean()),trial_rgb_mse=float(np.square(new-t).mean()),maximum_render_change_255=float(abs(old-new).max()),mean_render_change_255=float(abs(old-new).mean()))
    write(D/'regional-measurements.json',dict(method='RGB error in fixed rectangles, excluding background with common reference/model foreground. Not a perceptual score.',regions=regions))
    for name in ['full-comparison.png','head-comparison.png','collars-comparison.png','socket-comparison.png','base-comparison.png','contour-highres.png','contour-original.png','overlay-highres.png','overlay-original.png','metrics.json','validation.json','fit.json','parameters.json','fixed-response.exr','response-00.exr','response-01.exr','response-02.exr','response-03.exr','neutral.png','profile.png','rear.png','side.png']:
        shutil.copy2(O/name,D/name)
    for source,dest in [('scope-check.json','partition-preservation.json'),('legacy-regeneration.json','legacy-regeneration.json')]:shutil.copy2(ROOT/'build/king-mission/097-socket-partition-baseline'/source,D/dest)

    # Opposite-color originals remain geometry evidence; no white finish is inferred.
    original_colors_contact(D,O)
    write(D/'checkpoint.json',dict(checkpoint='009',status='candidate validated; pending visual acceptance and review synchronization',accepted_variant='103-socket-fitted-glints',previous_checkpoint='007',
        model_sha256=sha(O/'king.blend'),render_sha256=sha(O/'wood.png'),pigment_sha256=sha(ROOT/'assets/king/materials/king-pigment-atlas-v6.png'),
        scores=trials[-1]['scores'],original_iou_percent=trials[-1]['original_iou_percent'],equal_weight_mean=trials[-1]['equal_weight_mean'],holistic_visual_range_percent=[74,83],
        geometry_changed=False,material_changed=False,camera_elevation_degrees=read(O/'camera.json')['elevationDegrees'],receiver_count=5,added_lights=read(D/'scope-check.json')['added_lights'],
        mission_complete=False,validation=dict(reproduction=checks,scope='passed',receiver_regeneration='passed',export='passed',site='pending')))
    print('KING009_EVIDENCE_READY',flush=True)


if __name__=='__main__':main()
