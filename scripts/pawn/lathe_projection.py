"""Map the pawn's static cylindrical UV to the saved Cycles camera and depth."""
import numpy as np
from derive_wood import ramp, sample


def visible_tiles(profile, depth, camera, size):
    view = np.array(camera["worldToCamera"]).reshape(4, 4)
    projection = np.array(camera["projectionMatrix"]).reshape(4, 4) @ view
    width, height = camera["width"], camera["height"]
    theta = ((np.arange(size) + .5) / size + .25) * 2 * np.pi
    cs, sn = np.cos(theta), np.sin(theta)
    for first in range(0, size, 64):
        rows = np.arange(first, min(first + 64, size))
        v = 1 - (rows + .5) / size
        r, z, nr, nz = [np.interp(v, profile[:, 0], profile[:, i])[:, None] for i in (1, 2, 3, 4)]
        x, y = r * cs, r * sn

        def project(row):
            return row[0] * x + row[1] * y + row[2] * z + row[3]

        px = (project(projection[0]) + 1) * width / 2 - .5
        py = (1 - project(projection[1])) * height / 2 - .5
        dz = np.abs(sample(depth, px, py) + project(view[2]))
        facing = (nr * cs * view[2, 0] + nr * sn * view[2, 1] + nz * view[2, 2]) / np.maximum(np.hypot(nr, nz), .01)
        visible = (1 - ramp(dz, .008, .035)) * ramp(facing, .08, .48)
        yield rows, x, y, z, px, py, visible
