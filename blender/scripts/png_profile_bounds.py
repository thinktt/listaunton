"""Measure a transparent 8-bit RGBA PNG's visible profile without dependencies."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path


def profile_bounds(path: Path, threshold: int = 64) -> dict:
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Not a PNG: {path}')
    offset = 8
    chunks = []
    header = None
    while offset < len(raw):
        length = struct.unpack_from('>I', raw, offset)[0]
        kind = raw[offset+4:offset+8]
        payload = raw[offset+8:offset+8+length]
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', payload)
        elif kind == b'IDAT':
            chunks.append(payload)
        elif kind == b'IEND':
            break
        offset += 12 + length
    if header is None or header[2:] != (8, 6, 0, 0, 0):
        raise ValueError(f'Expected a non-interlaced 8-bit RGBA PNG: {path}')
    width, height = header[:2]
    pixels = zlib.decompress(b''.join(chunks))
    row_size = 1 + width * 4
    if len(pixels) != row_size * height:
        raise ValueError(f'Unexpected PNG data size: {path}')
    previous = bytearray(width)
    rows = []
    for y in range(height):
        start = y * row_size
        mode = pixels[start]
        encoded = pixels[start + 4:start + row_size:4]
        alpha = bytearray(width)
        left = width
        right = -1
        prior = 0
        for x, value in enumerate(encoded):
            above = previous[x]
            upper_left = previous[x-1] if x else 0
            if mode == 0:
                result = value
            elif mode == 1:
                result = value + prior
            elif mode == 2:
                result = value + above
            elif mode == 3:
                result = value + ((prior + above) // 2)
            elif mode == 4:
                estimate = prior + above - upper_left
                da, db, dc = abs(estimate-prior), abs(estimate-above), abs(estimate-upper_left)
                predictor = prior if da <= db and da <= dc else above if db <= dc else upper_left
                result = value + predictor
            else:
                raise ValueError(f'Unsupported PNG filter {mode}: {path}')
            prior = result & 255
            alpha[x] = prior
            if prior >= threshold:
                left = min(left, x)
                right = x
        rows.append((left, right))
        previous = alpha
    occupied = [y for y, (_, right) in enumerate(rows) if right >= 0]
    if not occupied:
        raise ValueError(f'No visible piece in {path}')
    top, bottom = occupied[0], occupied[-1]
    if top == 0 or bottom == height-1:
        raise ValueError(f'Profile appears clipped: {path}')
    visible_rows = rows[top:bottom+1]
    left = min(a for a, b in visible_rows if b >= 0)
    right = max(b for _, b in visible_rows)
    base_top = bottom - (bottom-top)//5
    base_rows = [row for row in rows[base_top:bottom+1] if row[1] >= 0]
    base_center = (min(a for a, _ in base_rows)+max(b for _, b in base_rows))/2
    return {'width': width, 'height': height, 'top': top, 'bottom': bottom,
            'left': left, 'right': right, 'center': base_center}
