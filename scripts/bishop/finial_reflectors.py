"""Apply the two measured specular reflectors restricted to the button surface."""
import math

import bpy

BUTTON = 'Bishop - domed button finial'
NAMES = {'button reflection', 'Button second glint'}


def apply_finial_reflectors(specifications):
    if len(specifications) != 2 or {s['name'] for s in specifications} != NAMES:
        raise ValueError('Expected the two existing button reflectors.')
    for spec in specifications:
        lamp = bpy.data.objects[spec['name']]
        assert lamp.data.type == 'AREA' and lamp.data.shape == spec['shape'] == 'ELLIPSE'
        assert not lamp.visible_diffuse and lamp.visible_glossy
        assert [o.name for o in lamp.light_linking.receiver_collection.objects] == [BUTTON]
        assert set(spec) == {'name', 'shape', 'location', 'rotation_euler', 'size', 'size_y', 'energy', 'color'}
        for key in ('location', 'rotation_euler', 'color'):
            assert len(spec[key]) == 3 and all(math.isfinite(v) for v in spec[key])
        assert all(0 <= v <= 1 for v in spec['color'])
        for key in ('size', 'size_y', 'energy'):
            assert math.isfinite(spec[key]) and spec[key] > 0
        lamp.location = spec['location']
        lamp.rotation_euler = spec['rotation_euler']
        for key in ('size', 'size_y', 'energy', 'color'):
            setattr(lamp.data, key, spec[key])
    bpy.context.view_layer.update()
