"""Check projection experiments without Blender; source closure is in Blender reports.

Run after every variant has been built, rendered, exported and validated:
    python scripts/king/check_projection_variants.py
The archived pre-mission king must still match baseline-preservation.json,
captured before the experiment. This checker does not rewrite the models or their fit results.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix16(values):
    if values and isinstance(values[0], list):
        values = [value for row in values for value in row]
    require(len(values) == 16 and all(math.isfinite(v) for v in values), 'Invalid camera matrix')
    return values


def check(root, manifest_file, baseline_file):
    def local(name):
        path = (root / name).resolve()
        require(path.is_relative_to(root), f'Asset escapes repository: {name}')
        require(path.is_file(), f'Missing asset: {name}')
        return path

    manifest = json.loads(manifest_file.read_text())
    baseline = json.loads(baseline_file.read_text())
    canonical = baseline['sha256']
    required_baseline = {'models/king/king-rebuilt.blend', 'assets/king/mesh.json', 'assets/king/mesh.bin', 'assets/king/render.png', 'assets/king/camera.json', 'assets/king/reference.png', 'assets/king/original.png', 'assets/king/validation.json'}
    require(required_baseline <= canonical.keys(), 'Preservation snapshot is incomplete')
    for name, expected in canonical.items():
        actual = sha(local('history/king-before-54-mission/' + name))
        if actual != expected and name in baseline.get('jsonContentSha256', {}):
            content = json.dumps(json.loads(local('history/king-before-54-mission/' + name).read_text()), sort_keys=True, separators=(',', ':')).encode()
            require(hashlib.sha256(content).hexdigest() == baseline['jsonContentSha256'][name], f'Canonical king data changed: {name}')
        else:
            require(actual == expected, f'Canonical king changed: {name}')

    variants = manifest['variants']
    require(len(variants) == 6, 'Expected six projection variants')
    require(sorted(v['elevation'] for v in variants) == [48, 52, 54, 56, 60, 64], 'Unexpected projection angles')
    require(len({v['id'] for v in variants}) == 6, 'Duplicate variant IDs')
    require(manifest['baseline'] in {v['id'] for v in variants}, 'Baseline variant missing')
    base_variant = next(v for v in variants if v['id'] == manifest['baseline'])
    require(base_variant['elevation'] == 52, 'Baseline must be the 52-degree king')

    reports = []
    for variant in variants:
        prefix = variant['assetDir'].rstrip('/')
        paths = {name: local(prefix + '/' + name) for name in ['mesh.bin', 'mesh.json', 'camera.json', 'render.png', 'profile.png', 'profile.json', 'qa.json', 'validation.json']}
        meta = json.loads(paths['mesh.json'].read_text())
        camera = json.loads(paths['camera.json'].read_text())
        validation = json.loads(paths['validation.json'].read_text())
        qa = json.loads(paths['qa.json'].read_text())
        json.loads(paths['profile.json'].read_text())
        model_hash = sha(local(variant['model']))
        require(meta['sourceSha256'] == model_hash, f"Stale mesh export: {variant['id']}")
        require(validation.get('source_hash_matches') is True, f"Unverified source hash: {variant['id']}")
        if 'sourceSha256' in validation:
            require(validation['sourceSha256'] == model_hash, f"Stale closure report: {variant['id']}")
        components = validation['components']
        require(len(components) == 2, f"Expected separate body and cross: {variant['id']}")
        for component in components:
            require(component['nonmanifold_edges'] == 0, f"Open component: {variant['id']} / {component['name']}")
            require(math.isfinite(component['signed_volume']) and component['signed_volume'] > 0, f"Invalid volume: {variant['id']} / {component['name']}")
            require(component['vertices'] > 0 and component['faces'] > 0, f"Empty component: {variant['id']}")

        binary = paths['mesh.bin'].read_bytes()
        require(meta['vertexStrideBytes'] == 24, 'Unexpected vertex layout')
        require(meta['vertexByteLength'] == meta['vertexCount'] * 24 == meta['indexByteOffset'], 'Vertex byte count mismatch')
        require(len(binary) == meta['totalByteLength'] == meta['indexByteOffset'] + meta['indexCount'] * 4, 'Binary export byte count mismatch')
        require(meta['indexCount'] == meta['triangleCount'] * 3, 'Triangle count mismatch')
        require(len(meta['parts']) == 2, 'Expected two exported parts')
        require(sum(p['triangleCount'] for p in meta['parts']) == meta['triangleCount'], 'Exported part counts mismatch')
        lows = [math.inf] * 3
        highs = [-math.inf] * 3
        normal_error = 0.0
        for values in struct.iter_unpack('<6f', binary[:meta['vertexByteLength']]):
            require(all(math.isfinite(value) for value in values), 'Non-finite vertex or normal')
            for axis, value in enumerate(values[:3]):
                lows[axis] = min(lows[axis], value)
                highs[axis] = max(highs[axis], value)
            normal_error = max(normal_error, abs(math.sqrt(sum(v*v for v in values[3:])) - 1))
        require(normal_error < 1e-3, f'Non-unit normals: {normal_error}')
        for (index,) in struct.iter_unpack('<I', binary[meta['indexByteOffset']:]):
            require(index < meta['vertexCount'], 'Out-of-bounds mesh index')
        size = [highs[i] - lows[i] for i in range(3)]
        center = [(highs[i] + lows[i]) / 2 for i in range(3)]
        for field, actual in [('min', lows), ('max', highs), ('size', size), ('center', center)]:
            require(max(abs(a-b) for a,b in zip(actual,meta['bounds'][field])) < 1e-5, f"Incorrect {field} bounds: {variant['id']}")
        require(min(size) > 0 and abs(size[0] - size[1]) < .001, f"Base dimensions invalid: {variant['id']}")
        if 'heightDiameter' in variant:
            require(abs(variant['heightDiameter'] - size[2]/size[0]) < .015, f"Height/diameter label mismatch: {variant['id']}")

        require(camera['type'] == meta['referenceCamera']['type'] == 'ORTHO', 'Projection must be orthographic')
        world = matrix16(camera['worldToCamera'])
        projection = matrix16(camera['projectionMatrix'])
        for field in ['worldToCamera', 'projectionMatrix']:
            require(max(abs(a-b) for a,b in zip(matrix16(camera[field]), matrix16(meta['referenceCamera'][field]))) < 1e-7, 'Render/export camera mismatch')
        elevation = math.degrees(math.atan2(abs(world[10]), math.hypot(world[8], world[9])))
        require(abs(elevation - variant['elevation']) < .01, f"Wrong saved camera: {variant['id']} = {elevation}")
        require(camera['width'] == camera['height'] == 1254, 'Unexpected render canvas')
        require(abs(projection[12]) + abs(projection[13]) + abs(projection[14]) < 1e-6 and abs(projection[15]-1) < 1e-6, 'Non-orthographic projection matrix')
        require(camera['orthoScale'] > 0, 'Invalid orthographic scale')
        for name in ['render.png', 'profile.png']:
            png = paths[name].read_bytes()
            require(png[:8] == b'\x89PNG\r\n\x1a\n' and png[12:16] == b'IHDR', f'Invalid PNG: {name}')
            width, height = struct.unpack('>II', png[16:24])
            require(width > 0 and height > 0, 'Empty image canvas')
            if name == 'render.png':
                require((width, height) == (camera['width'], camera['height']), 'Render/camera dimensions mismatch')
            try:
                from PIL import Image
            except ImportError:
                pass
            else:
                with Image.open(paths[name]) as image:
                    image.verify()
        for key, source_name in [('original', 'assets/king/original.png'), ('selected', 'assets/king/reference.png')]:
            fit = qa['images'][key]
            require(fit['reference_sha256'] == canonical[source_name], f'Source changed in {key} fit')
            require(0 <= fit['silhouette_iou'] <= 1, 'Invalid IoU')
            require(all(math.isfinite(fit[k]) and fit[k] >= 0 for k in ['mean_boundary_error_px', 'p95_boundary_error_px']), 'Invalid boundary score')
        reports.append({'id':variant['id'], 'elevation':elevation, 'modelSha256':model_hash, 'meshSha256':sha(paths['mesh.bin']), 'renderSha256':sha(paths['render.png']), 'triangleCount':meta['triangleCount'], 'baseDiameter':size[0], 'height':size[2], 'heightDiameter':size[2]/size[0], 'closedComponents':len(components), 'originalSilhouetteIoU':qa['images']['original']['silhouette_iou']})

    require(len({r['triangleCount'] for r in reports}) == 1, 'Variants have different mesh topology counts')
    require(len({r['modelSha256'] for r in reports}) == 6, 'Duplicate model file in projection experiment')
    require(len({r['meshSha256'] for r in reports}) == 6, 'Geometry was not regenerated for each projection')
    require(len({r['renderSha256'] for r in reports}) == 6, 'Duplicate variant render')
    canonical_meta = json.loads(local('history/king-before-54-mission/assets/king/mesh.json').read_text())
    for source in ['assets/king/reference.png', 'assets/king/original.png']:
        require(sha(local(source)) == canonical[source], 'Current source reference changed: '+source)
    base_width = canonical_meta['bounds']['size'][0]
    for result in reports:
        require(abs(result['baseDiameter']/base_width - 1) < .025, f"Physical base scale changed more than 2.5%: {result['id']}")
    shared = manifest.get('sharedView')
    if shared:
        require(len(shared['center']) == 3 and all(math.isfinite(x) for x in shared['center']), 'Invalid shared-view center')
        require(shared['orthoHeight'] > 0 and shared['distance'] > 0, 'Invalid common inspection camera')
    return {'passed':True, 'historicalKingBaselineUnchanged':True,'baselineArchive':'history/king-before-54-mission', 'preservedCanonicalFiles':sorted(canonical), 'expectedElevations':[48,52,54,56,60,64], 'physicalBaseDiameterTolerancePercent':2.5, 'closureEvidence':'Blender validation reports certify the two source components. This checker verifies hashes and exported binary structure; it does not infer manifoldness from duplicated viewer vertices.', 'variants':reports}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--baseline', type=Path)
    args=parser.parse_args()
    root=args.root.resolve()
    directory=root/'assets/king-projections'
    report=check(root, args.manifest or directory/'variants.json', args.baseline or directory/'baseline-preservation.json')
    (directory/'check-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
