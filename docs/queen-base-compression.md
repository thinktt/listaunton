# Queen base compression

Open **Base studies** on the queen review to compare the accepted raised socket from checkpoint 18 with a vertically compressed version. The study uses the same wood atlas, studio lights, 54° camera, foot width and ground line for both.

In the compressed version, every control ring from the bottom of the foot through the stem seat has 88% of its former height above the floor. This squashes the foot, groove, flare and raised socket in one operation. Every horizontal control coordinate is preserved. The lower stem absorbs the difference with a smooth transition so the crown stays registered.

| Height in Blender units | Raised socket | Compressed |
| --- | ---: | ---: |
| Foot groove above the floor | 0.2495 | 0.2195 |
| Flare-to-socket join above the floor | 0.9440 | 0.8307 |
| Stem seat above the floor | 1.3094 | 1.1523 |
| Straight socket wall | 0.1470 | 0.1294 |

The original black sprite gives silhouette overlap of 97.91% for the raised socket and 97.08% for the compressed version. The selected high-resolution reference gives 97.97% and 97.62%. The lower position of the shoulder is easier to judge in the side profiles or by blinking the fixed overlay. The percentages describe the outer outline.

Both editable Blender files are in `models/queen-base-studies/`. The frozen `socket.blend` is checkpoint 18. The `compressed.blend` file is the alternative. The model generator verifies the original horizontal coordinates and height scaling. The export checks verify the fixed camera, shared dimensions, UVs and Blender mesh bytes. The browser test compares GPU buffer contents with both exports while holding the orbit steady.

Rebuild from the repository root with Blender, Python with NumPy and Pillow, and the tracked reference images.

```sh
blender -b --python-exit-code 1 --python scripts/queen/build_base_study.py
blender -b --python-exit-code 1 --python scripts/queen/render_base_study.py
for id in socket compressed; do
  blender -b --python-exit-code 1 --python scripts/queen/export_viewer_mesh.py -- \
    --blend "models/queen-base-studies/$id.blend" \
    --binary "build/queen-base-studies/$id/mesh.bin" \
    --metadata "build/queen-base-studies/$id/mesh.json"
done
python scripts/queen/build_base_viewer.py
python scripts/queen/compare_base_studies.py
```

The recorded measurements and browser check are in `assets/queen-base-studies/`. To repeat the browser check with Playwright available and the site running locally, run `node scripts/queen/check_base_studies.cjs http://localhost:8080/`.
