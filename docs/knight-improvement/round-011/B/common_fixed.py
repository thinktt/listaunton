"""Isolate the physical eye change with the parent studio and common neutral clay."""
from pathlib import Path
import json
import sys
import bpy
from mathutils import Matrix

sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from carve import border, configure_render, flat, load, render, sha

names = ['Eye reflection upper', 'Eye reflection lower']


def setup(s):
    configure_render(s, 64)
    s.cycles.device='CPU'
    s.render.threads_mode='FIXED'
    s.render.threads=4
    border(s, (448, 444, 565, 524))


def retrieve(s):
    values={}
    for name in names:
        o=s.objects[name]
        light=o.data
        receiver=o.light_linking.receiver_collection
        values[name]={
            'matrix': [list(row) for row in o.matrix_world],
            'shape': light.shape, 'energy': light.energy, 'color': list(light.color),
            'size': light.size, 'size_y': light.size_y, 'spread': light.spread,
            'receivers': None if receiver is None else [x.name for x in receiver.objects]}
    return values


def transfer(s, values):
    for name, config in values.items():
        o=s.objects[name]
        o.matrix_world=Matrix(config['matrix'])
        for key in ['shape','energy','color','size','size_y','spread']:
            setattr(o.data, key, config[key])
        if config['receivers'] is None:
            o.light_linking.receiver_collection=None
        else:
            coll=bpy.data.collections.new('Comparison receivers '+name)
            for part in config['receivers']:
                coll.objects.link(s.objects[part])
            o.light_linking.receiver_collection=coll
    bpy.context.view_layer.update()


def main():
    lamps=retrieve(load('parent.blend'))
    data={}
    for text, file in [('parent','parent.blend'), ('B','knight.blend')]:
        s=load(file)
        setup(s)
        if text=='B':
            transfer(s,lamps)
        for finish in ['walnut','clay']:
            if finish=='clay':
                flat(s)
            target=D/f'common-fixed-{text}-{finish}.png'
            render(s,target)
            data[target.name]=sha(target)
    (D/'common-fixed.json').write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
