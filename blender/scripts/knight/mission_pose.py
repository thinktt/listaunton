"""Shared, height-preserving XY placement of the carving on the turned base."""
import numpy as np


def bend_weight(z):
    t = np.clip((z - 1.68) / (3.55 - 1.68), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def posed(points, dx, dy, twist_degrees):
    result = points.copy()
    weight = bend_weight(points[:, 2])
    angle = np.radians(twist_degrees) * weight
    cos, sin = np.cos(angle), np.sin(angle)
    x, y = points[:, 0], points[:, 1]
    result[:, 0] = cos * x - sin * y + weight * dx
    result[:, 1] = sin * x + cos * y + weight * dy
    return result
