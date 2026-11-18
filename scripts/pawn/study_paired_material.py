"""Compare a static material in the saved reference and side-studio scenes."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,sha,render,setup,save_json
from polish_trial import open_source

def attach(scene,body,row):
    if row.get('pigment'):
        path=ROOT/row['pigment']
        assert sha(path)==row['pigment_sha256']
        node=body.data.materials[0].node_tree.nodes['Pawn walnut pigment']
        previous=node.image
        node.image=bpy.data.images.load(str(path),check_existing=False)
        node.image.colorspace_settings.name='sRGB';node.image.pack()
        if previous.users==0:bpy.data.images.remove(previous)
        scene['pawn_texture_path']=row['pigment']
        scene['pawn_texture_sha256']=row['pigment_sha256']
    for spec in row.get('maps',[]):
        path=ROOT/spec['path'];assert sha(path)==spec['sha256']
        nodes=body.data.materials[0].node_tree.nodes
        if spec.get('node'):found=[nodes[spec['node']]]
        else:
            import hashlib
            found=[n for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.packed_file and hashlib.sha256(n.image.packed_file.data).hexdigest()==spec['old_sha256']]
        assert found
        image=bpy.data.images.load(str(path),check_existing=False)
        image.colorspace_settings.name=spec['encoding'];image.pack()
        for node in found:node.image=image
        prefix={'Pawn varnish roughness':'pawn_roughness','Pawn fine slope atlas':'pawn_slope'}.get(spec.get('node'))
        if prefix:
            scene[prefix+'_path']=spec['path'];scene[prefix+'_sha256']=spec['sha256']
        elif not spec.get('node'):
            scene['pawn_hidden_relief_path']=spec['path'];scene['pawn_hidden_relief_sha256']=spec['sha256']

def run(cfg):
    results={}
    for row in cfg['variants']:
        scene,body=open_source(cfg)
        attach(scene,body,row)
        if row.get('profile_rz'):
            from study_side_quality import profile_edit
            profile_edit(body,row['profile_rz'])
        out=ROOT/cfg['output']/row['name'];out.mkdir(parents=True,exist_ok=True)
        scene['pawn_material_study']=json.dumps(row,sort_keys=True)
        scene.render.filepath=str(out/'fixed.png')
        side=bpy.data.scenes[scene['pawn_side_scene']]
        assert body in list(side.objects)
        setup(side,cfg.get('samples',128))
        side.render.resolution_x=side.render.resolution_y=cfg.get('side_resolution',900)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'pawn.blend'))
        bpy.context.window.scene=scene;render(scene,out/'fixed.png')
        bpy.context.window.scene=side;render(side,out/'side.png')
        if row.get('clay'):
            wood=body.data.materials[0]
            clay=bpy.data.materials.new('Paired-study clay');clay.use_nodes=True
            bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.24,.27,.3,1);bs.inputs['Roughness'].default_value=.4
            body.data.materials[0]=clay;render(side,out/'clay.png');body.data.materials[0]=wood
        results[row['name']]={k:sha(out/k) for k in ('pawn.blend','fixed.png','side.png')}
        print('PAIRED_MATERIAL_DONE',row['name'],flush=True)
    save_json(ROOT/cfg['output']/'study.json',{'config':cfg,'results':results})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text()))
