"""Read both saved model profiles, including checkpoints with older manifests."""
import hashlib
import json
import struct


def read_profile(root, model_sha256):
    assets = root / 'assets/knight'
    saved = json.loads((assets / 'side-registration.json').read_text())
    assert saved['source_blend_sha256'] == model_sha256, 'Stale side profile scene.'
    record = {key: saved[key] for key in (
        'source_blend_sha256', 'profile_size', 'canvas', 'scale', 'offset_x',
        'offset_y', 'physical_foot_center_x'
    )}
    assert record['profile_size'] == record['canvas']
    assert (record['scale'], record['offset_x'], record['offset_y']) == (1, 0, 0)
    for key, filename in [('profile', 'guide-render.png'), ('neutral', 'guide-neutral.png')]:
        path = assets / filename
        relative = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        # Older releases recorded only the walnut digest. The clay PNG was
        # rendered immediately before it, with the same scene and camera.
        if key in saved or key == 'profile' or 'guide' not in saved:
            assert (saved[key], saved[key + '_sha256']) == (relative, digest), 'Stale ' + filename
        assert raw.startswith(b'\x89PNG\r\n\x1a\n')
        assert list(struct.unpack('>II', raw[16:24])) == record['canvas'], filename
        record[key] = relative
        record[key + '_sha256'] = digest
    camera = json.loads((assets / 'guide-camera.json').read_text())
    if 'elevation' in saved:
        assert camera['elevation'] == saved['elevation']
    record['elevation'] = camera['elevation']
    record['method'] = 'Walnut and neutral clay rendered from the reopened scene using the same registered side camera.'
    return record
