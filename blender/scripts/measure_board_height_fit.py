"""Measure the visible wood-colored top and foot of each original board piece.

Print measured coordinates; --check verifies the recorded height-fit.json.
Uses only the Python standard library and the two supplied PNG screenshots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'assets/board-comparison'
ORDER = ('king', 'queen', 'bishop', 'knight', 'rook', 'pawn')


def rgba_rows(path: Path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Not a PNG: {path}')
    offset, chunks, header = 8, [], None
    while offset < len(data):
        size = struct.unpack_from('>I', data, offset)[0]
        kind, payload = data[offset+4:offset+8], data[offset+8:offset+8+size]
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', payload)
        elif kind == b'IDAT':
            chunks.append(payload)
        elif kind == b'IEND':
            break
        offset += size + 12
    if header is None or header[2:] != (8, 6, 0, 0, 0):
        raise ValueError('Expected a non-interlaced 8-bit RGBA PNG')
    width, height = header[:2]
    pixels = zlib.decompress(b''.join(chunks))
    stride = width * 4
    if len(pixels) != (stride + 1) * height:
        raise ValueError('Unexpected PNG data length')
    previous = bytearray(stride)
    rows = []
    for y in range(height):
        start = y * (stride + 1)
        mode, source = pixels[start], pixels[start+1:start+1+stride]
        row = bytearray(stride)
        for i, value in enumerate(source):
            left = row[i-4] if i >= 4 else 0
            above = previous[i]
            upper_left = previous[i-4] if i >= 4 else 0
            if mode == 0:
                predictor = 0
            elif mode == 1:
                predictor = left
            elif mode == 2:
                predictor = above
            elif mode == 3:
                predictor = (left + above) // 2
            elif mode == 4:
                guess = left + above - upper_left
                a, b, c = abs(guess-left), abs(guess-above), abs(guess-upper_left)
                predictor = left if a <= b and a <= c else above if b <= c else upper_left
            else:
                raise ValueError(f'Unsupported PNG filter {mode}')
            row[i] = (value + predictor) & 255
        rows.append(row)
        previous = row
    return width, height, rows


def measure():
    width, height, original = rgba_rows(DIRECTORY / 'original-lineup.png')
    blank_width, blank_height, empty = rgba_rows(DIRECTORY / 'empty-board.png')
    if (width, height) != (659, 202) or (blank_width, blank_height) != (width, height):
        raise ValueError('Unexpected screenshot size')
    result = {}
    for index, piece in enumerate(ORDER):
        left, right = index*width//6, (index+1)*width//6
        occupied = []
        for y in range(height):
            count = 0
            for x in range(left, right):
                i = 4*x
                r, g, b = original[y][i:i+3]
                er, eg, eb = empty[y][i:i+3]
                difference = abs(r-er) + abs(g-eg) + abs(b-eb)
                if difference >= 30 and r >= b*1.12 and r >= g*1.03:
                    count += 1
            if count >= 3:
                occupied.append(y)
        if not occupied:
            raise ValueError(f'No visible wood pixels found for {piece}')
        result[piece] = {'top': occupied[0], 'bottom': occupied[-1]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = measure()
    if args.check:
        record = json.loads((DIRECTORY / 'height-fit.json').read_text(encoding='utf-8'))
        for filename, key in [('original-lineup.png', 'original_sha256'), ('empty-board.png', 'empty_board_sha256')]:
            if hashlib.sha256((DIRECTORY / filename).read_bytes()).hexdigest() != record[key]:
                raise ValueError(f'{filename} changed')
        if result != record['targets']:
            raise ValueError(f'Measured heights differ from the saved fit: {result}')
        print('PASS: screenshot hashes and all six recorded visible heights.')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
