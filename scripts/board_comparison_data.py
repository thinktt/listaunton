"""Project current Blender renders uniformly onto the owner's board screenshot."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path
from png_profile_bounds import profile_bounds

RENDERS = {
    'king': 'assets/king/render.png',
    'queen': 'assets/queen/queen-brown.png',
    'bishop': 'assets/bishop/render.png',
    'knight': 'assets/knight/render.png',
    'rook': 'assets/rook/render.png',
    'pawn': 'assets/pawn/render.png',
}
CENTERS = {'king': 55.5, 'queen': 164.0, 'bishop': 274.5,
           'knight': 385.5, 'rook': 493.5, 'pawn': 604.0}


def png_size(path: Path) -> tuple[int, int]:
    with path.open('rb') as stream:
        header = stream.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError(f'Expected PNG: {path}')
    return struct.unpack('>II', header[16:24])


def script_text(document: str, ident: str) -> str:
    match = re.search(r'<script id="' + re.escape(ident) + r'"[^>]*>(.*?)</script>', document, re.S)
    if not match:
        raise ValueError(f'Missing {ident} in queen review')
    return match.group(1)


def source_meta(root: Path, piece: str) -> dict:
    if piece != 'queen':
        return json.loads((root / f'assets/{piece}/mesh.json').read_text(encoding='utf-8'))
    review = (root / 'review.html').read_text(encoding='utf-8')
    viewer = json.loads(script_text(review, 'viewer-document'))
    return json.loads(script_text(viewer, 'mesh-metadata'))


def projected_foot(meta: dict) -> tuple[float, float, float]:
    camera = meta['referenceCamera']
    if camera['type'] != 'ORTHO':
        raise ValueError('Board comparison expects orthographic reference cameras')
    matrix = camera['worldToCamera']
    projection = camera['projectionMatrix']
    elevation = math.degrees(math.atan2(abs(matrix[10]), abs(matrix[6])))
    if abs(elevation - 54) > 0.05:
        raise ValueError(f'Expected a 54-degree camera, got {elevation:.3f}')
    foot = [0, 0, meta['bounds']['min'][2], 1]
    camera_point = [sum(matrix[4*i+j] * foot[j] for j in range(4)) for i in range(4)]
    clip = [sum(projection[4*i+j] * camera_point[j] for j in range(4)) for i in range(4)]
    width, height = camera['width'], camera['height']
    x = (clip[0] / clip[3] + 1) * width / 2
    y = (1 - clip[1] / clip[3]) * height / 2
    return x, y, abs(projection[0]) * width / 2


def build_board_data(root: Path) -> dict:
    original = 'assets/board-comparison/original-lineup.png'
    empty = 'assets/board-comparison/empty-board.png'
    if png_size(root / original) != (659, 202) or png_size(root / empty) != (659, 202):
        raise ValueError('Expected the two supplied 659×202 board screenshots')
    fit = json.loads((root / 'assets/board-comparison/height-fit.json').read_text(encoding='utf-8'))
    if hashlib.sha256((root / original).read_bytes()).hexdigest() != fit['original_sha256'] or hashlib.sha256((root / empty).read_bytes()).hexdigest() != fit['empty_board_sha256']:
        raise ValueError('Board screenshots changed; remeasure the matched heights')
    if set(fit['targets']) != set(RENDERS):
        raise ValueError('Height fit must include all six pieces')
    metas = {piece: source_meta(root, piece) for piece in RENDERS}
    king = metas['king']
    king_height = king['bounds']['size'][2]
    # The screenshot's king base is about 86 pixels wide at its widest row.
    king_pixels_per_unit = 86.0 / king['bounds']['size'][0]
    pieces = []
    for piece, filename in RENDERS.items():
        meta = metas[piece]
        camera = meta['referenceCamera']
        width, height = png_size(root / filename)
        if (width, height) != (camera['width'], camera['height']):
            raise ValueError(f'{piece} render dimensions do not match its saved camera')
        x, y, pixels_per_unit = projected_foot(meta)
        visible = profile_bounds(root / filename)
        target = fit['targets'][piece]
        if target['bottom'] <= target['top'] or visible['bottom'] <= visible['top']:
            raise ValueError(f'Invalid height-fit bounds for {piece}')
        pieces.append({'piece': piece, 'file': filename,
                       'version': hashlib.sha256((root / filename).read_bytes()).hexdigest()[:16],
                       'width': width, 'height': height, 'footX': x, 'footY': y,
                       'pixelsPerUnit': pixels_per_unit, 'modelHeight': meta['bounds']['size'][2],
                       'baseWidth': meta['bounds']['size'][0] if piece != 'knight' else meta['bounds']['size'][1],
                       'centerX': CENTERS[piece], 'sourceSha256': meta['sourceSha256'],
                       'renderTop': visible['top'], 'renderBottom': visible['bottom'],
                       'targetTop': target['top'], 'targetBottom': target['bottom']})
    return {'width': 659, 'height': 202, 'original': original, 'empty': empty,
            'kingHeight': king_height, 'kingPixelsPerUnit': king_pixels_per_unit,
            'groundY': 151.0, 'kingBasePixels': 86.0, 'pieces': pieces}
