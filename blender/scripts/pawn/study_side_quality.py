"""Compare real lathe profiles in the fixed reference rig and a shared side studio.

The studio changes lighting only. Every angle uses the same actual wood and
geometry; the reference-camera render retains the original 47-light rig.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,control,fixed_camera,render,side_camera,area,save_json,sha,setup
from polish_trial import open_source

def profile_edit(body,points):
    co=np.array([v.co[:] for v in body.data.vertices],dtype=np.float32).reshape(-1,96,3)
    before=co.copy()
    for key,point in points.items():
        i=int(key);radius,z=point
        if radius is not None:co[i,:,:2]*=(radius/np.linalg.norm(co[i,:,:2],axis=1))[:,None]
        if z is not None:co[i,:,2]=z
    body.data.vertices.foreach_set('co',co.ravel());body.data.update()
    return {str(i):{'before':before[i,0].tolist(),'after':co[i,0].tolist()} for i in map(int,points)}

def studio(scene,style='broad'):
    for o in list(scene.objects):
        if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
    bg=scene.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.6,.65,.72,1);bg.inputs['Strength'].default_value=.28
    if style in ('warm','balanced'):
        balanced=style=='balanced'
        bg.inputs['Color'].default_value=(.78,.82,.88,1);bg.inputs['Strength'].default_value=.08 if balanced else .10
        area(scene,'Studio key',(-3,-4,6),(0,0,1.4),240 if balanced else 260,1.7,color=(1,.93,.83))
        area(scene,'Studio fill',(4,-4,3.5),(0,0,1.3),140 if balanced else 160,2.6,color=(1,.96,.9))
        area(scene,'Studio rim',(1,3,4.5),(0,0,1.4),90 if balanced else 140,2,color=(1,.97,.92))
        area(scene,'Studio diffuse card',(0,-4,2.5),(0,0,1.4),230 if balanced else 360,5,color=(1,.91,.8),glossy=False)
        area(scene,'Studio lower bounce',(-1,-3,.65),(0,0,1.5),65 if balanced else 90,2.5,color=(1,.9,.78),glossy=False)
        return
    if style=='rounded':
        bg.inputs['Color'].default_value=(.78,.82,.88,1);bg.inputs['Strength'].default_value=.45
        area(scene,'Studio key',(-3,-4,6),(0,0,1.4),210,1.7,color=(1,.95,.88))
        area(scene,'Studio fill',(4,-3,3.5),(0,0,1.3),130,2.6,color=(.93,.96,1))
        area(scene,'Studio rim',(1,3,4.5),(0,0,1.4),180,2,color=(1,.97,.92))
        return
    area(scene,'Studio key',(-3.4,-4.5,5.2),(0,0,1.4),340,3.8,color=(1,.93,.84),size_y=2.8)
    area(scene,'Studio fill',(3.5,-2.8,3.1),(0,0,1.3),145,4,color=(.86,.92,1),size_y=3.2)
    area(scene,'Studio rim',(1.8,2.3,4.2),(0,0,1.4),300,2.4,color=(1,.96,.88),size_y=3)

def run(cfg):
    root=ROOT/'build/pawn-side-quality'/cfg['study'];root.mkdir(parents=True,exist_ok=True)
    report={'config':cfg,'variants':{}}
    for row in cfg['variants']:
        scene,body=open_source({**cfg,'samples':cfg.get('samples',192)})
        if row.get('pigment'):
            path=ROOT/row['pigment'];assert sha(path)==row['pigment_sha256']
            node=body.data.materials[0].node_tree.nodes['Pawn walnut pigment']
            previous=node.image;node.image=bpy.data.images.load(str(path),check_existing=False)
            node.image.colorspace_settings.name='sRGB';node.image.pack()
            if previous.users==0:bpy.data.images.remove(previous)
            scene['pawn_texture_path']=row['pigment'];scene['pawn_texture_sha256']=row['pigment_sha256']
        if row.get('bump'):
            path=ROOT/row['bump'];assert sha(path)==row['bump_sha256']
            nodes=body.data.materials[0].node_tree.nodes
            found=[n for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.packed_file and hashlib.sha256(n.image.packed_file.data).hexdigest()==row['bump_source_sha256']]
            assert found
            image=bpy.data.images.load(str(path),check_existing=False);image.colorspace_settings.name='sRGB';image.pack()
            for node in found:node.image=image
            scene['pawn_hidden_relief_path']=row['bump'];scene['pawn_hidden_relief_sha256']=row['bump_sha256']
        edits=profile_edit(body,row.get('profile_rz',{}));fixed_camera(scene)
        out=root/row['name'];out.mkdir(parents=True,exist_ok=True)
        scene['pawn_side_quality_trial']=json.dumps(row,sort_keys=True)
        scene.render.filepath=str(out/'fixed.png')
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'pawn.blend'));render(scene,out/'fixed.png')
        side_camera(scene);scene.render.resolution_x=scene.render.resolution_y=900
        render(scene,out/'side-original-rig.png')
        studio(scene,row.get('studio','broad'));render(scene,out/'side-studio.png')
        if row.get('diagnostics'):
            material=body.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
            output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
            old=output.inputs['Surface'].links[0].from_socket
            emit=nodes.new('ShaderNodeEmission');links.new(nodes['Pawn walnut pigment'].outputs['Color'],emit.inputs['Color']);links.new(emit.outputs[0],output.inputs['Surface'])
            render(scene,out/'diagnostic-albedo.png');links.new(old,output.inputs['Surface']);nodes.remove(emit)
        wood=body.data.materials[0];clay=bpy.data.materials.new('Side-quality neutral clay');clay.use_nodes=True
        bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.24,.27,.3,1);bs.inputs['Roughness'].default_value=.4
        body.data.materials[0]=clay;render(scene,out/'side-clay.png');body.data.materials[0]=wood
        report['variants'][row['name']]={'edits':edits,'model_sha256':sha(out/'pawn.blend'),
            'renders':{n:sha(out/(n+'.png')) for n in ('fixed','side-original-rig','side-studio','side-clay')}}
        print('SIDE_QUALITY_TRIAL_DONE',row['name'],flush=True)
    save_json(root/'study.json',report)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))
