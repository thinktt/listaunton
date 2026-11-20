"""Install the restored native surface pigment in the actual knight and render it."""
from pathlib import Path
import hashlib,json,shutil,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from evidence import load,flat_views,studio
from diagnostics import camera,diagnostics
from mission_scene import configure_render,render,save_model,sha
from map import MANE
PARENT='eaecb543e309c713db12fc83888bb2ffc0142686a06917ee6c76d24e7d2b2188'
ATLAS='1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b'
FILENAME='wood-atlas-improvement-014-B.png'
def install(s,file):
    node=s.objects['Knight | '+MANE].active_material.node_tree.nodes['Knight delivered albedo']
    old=node.image;assert hashlib.sha256(bytes(old.packed_file.data)).hexdigest()==ATLAS
    tex=bpy.data.images.load(str(file),check_existing=False);tex.colorspace_settings.name='sRGB';tex.pack()
    h=hashlib.sha256(bytes(tex.packed_file.data)).hexdigest();assert h==sha(file)
    tex.name='Knight walnut | restored mane figure 014-B';tex.filepath='//../../assets/knight/'+FILENAME
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image==old:n.image=tex
    if old.users==0:bpy.data.images.remove(old)
    s['knight_atlas_sha256']=h
def emission(s):
    for m in bpy.data.materials:
        if not m.node_tree:continue
        nt=m.node_tree;node=nt.nodes.get('Knight delivered albedo')
        if not node:continue
        emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(node.outputs['Color'],emit.inputs['Color'])
        nt.links.new(emit.outputs[0],nt.nodes['Material Output'].inputs['Surface'])
def crop(s,box):
    x,y,a,b=box;s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=(x+.05)/1254;s.render.border_max_x=(a+.05)/1254
    s.render.border_min_y=(1254-b+.05)/1254;s.render.border_max_y=(1254-y+.05)/1254
def get(key):
    s=load(('knight' if key=='knight' else 'parent')+'.blend')
    if key.isdigit():install(s,D/f'atlas-{key}.png')
    return s
def cpu(s,samples):
    configure_render(s,samples);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6
def trial(key):
    s=get(key);cpu(s,42);crop(s,(175,374,436,716))
    render(s,D/f'trial-{key}-wood.png')
    emission(s);render(s,D/f'trial-{key}-pigment.png')
def neutral(key):
    s=get(key);cpu(s,48);crop(s,(175,374,436,716))
    mat=s.objects['Knight | '+MANE].active_material;nt=mat.node_tree
    for node in nt.nodes:
        if node.type!='BSDF_PRINCIPLED':continue
        color=node.inputs['Base Color']
        for link in list(color.links):nt.links.remove(link)
        color.default_value=(.12,.12,.12,1.)
    render(s,D/f'neutral-{key}.png')
def turns(key):
    s=get(key);cpu(s,28)
    s.render.resolution_x=s.render.resolution_y=480
    yaw=json.loads(s['knight_mission_pose'])['twist_degrees']
    for mode in ('wood','pigment'):
        if mode=='pigment':emission(s)
        for name,theta in [('near',0),('rear-near',315),('rear',270),('rear-far',225),('far',180)]:
            camera(s,yaw+theta);render(s,D/f'turn-{key}-{mode}-{name}.png')
def save(i):
    assert sha(D/'parent.blend')==PARENT and sha(D/'parent-pigment.png')==ATLAS
    recipe=json.loads((D/f'restoration-{i}.json').read_text())
    shutil.copyfile(D/f'atlas-{i}.png',D/'pigment.png');assert sha(D/'pigment.png')==recipe['sha256']
    s=load('parent.blend');install(s,D/'pigment.png')
    settings={'recipe':i,'restoration':recipe,'parent_sha256':PARENT,'parent_pigment_sha256':ATLAS,
        'release_texture':FILENAME,'pigment_sha256':recipe['sha256']}
    s['knight_improvement_014_B']=json.dumps(settings)
    configure_render(s,144);save_model(s,D/'knight.blend');settings['model_sha256']=sha(D/'knight.blend')
    (D/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n');print(settings['model_sha256'],flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if args[0]=='trial':
        for i in args[1:]:trial(i)
    if args[0]=='turn':
        for i in args[1:]:turns(i)
    if args[0]=='neutral':
        for i in args[1:]:neutral(i)
    if args[0]=='save':save(int(args[1]))
    if 'studio' in args:studio()
    if 'orbit' in args:
        flat_views('knight.blend','');s=load('knight.blend');configure_render(s,32);diagnostics(s,'',True)
