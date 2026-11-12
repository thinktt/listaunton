"""Compare untouched receiver normals and sampling around a partition discrepancy."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu

def main():
    out=ROOT/'build/king-mission/120-collar-partition-diagnostic';out.mkdir(parents=True,exist_ok=True)
    paths=[ROOT/'history/king-mission-010/king-rebuilt.blend',ROOT/'build/king-mission/116-collar-partition-baseline/king.blend']
    digests=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    normals=[];responses={}
    for label,path in zip(['accepted','partition'],paths):
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;gpu(s)
        normals.append({o['king_render_region']:np.array([n.vector[:] for n in o.data.corner_normals],dtype=np.float32)
                        for o in s.objects if o.get('king_render_region') and o['king_render_region']!='upper-body' and 'collar' not in o['king_render_region']})
        w=s.render.resolution_x;h=s.render.resolution_y
        s.render.use_border=True;s.render.use_crop_to_border=False
        s.render.border_min_x=440/w;s.render.border_max_x=550/w
        s.render.border_min_y=1-780/h;s.render.border_max_y=1-730/h
        s.cycles.samples=1024;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
        s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
        s.render.use_persistent_data=True
        for bounces in [4,0]:
            s.cycles.glossy_bounces=bounces;name=f'{label}-bounces-{bounces}'
            dest=out/(name+'.exr');s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
            im=bpy.data.images.load(str(dest),check_existing=False);a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();bpy.data.images.remove(im)
            responses[name]=a[730:780,440:550]
    normcheck={name:dict(shape_exact=normals[0][name].shape==normals[1][name].shape,byte_exact=bool(np.array_equal(normals[0][name],normals[1][name])),max_error=float(abs(normals[0][name]-normals[1][name]).max())) for name in normals[0]}
    diffs={}
    for bounces in [4,0]:
        a=responses[f'accepted-bounces-{bounces}'];b=responses[f'partition-bounces-{bounces}'];delta=abs(a-b)
        diffs[str(bounces)]=dict(max_linear_error=float(delta.max()),mean_linear_error=float(delta.mean()),alpha_exact=bool(np.array_equal(a[:,:,3],b[:,:,3])))
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]==digests
    report=dict(source_hashes=digests,source_files_unchanged=True,unchanged_receiver_normals=normcheck,
                diagnostic_sampling=dict(samples=1024,adaptive=False,denoising=False,bounds=[440,730,550,780]),render_differences=diffs)
    (out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
