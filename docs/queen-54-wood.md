# Previous queen reconstruction at 54 degrees

This describes the previous revision, archived under `history/queen-before-scratch`. For the current fresh queen see [the new reconstruction notes](queen-side-rebuild.md).

The current queen is a revised version of the earlier 54-degree study. The
saved orthographic reference camera is **54 degrees above the board**, an
assumption used for the reconstruction rather than a recovered camera fact.
The side-view target is the owner's saved queen height of **83.4% of the
king**. To translate that cross-piece preference into a physical model size,
we normalize the 54-degree king model by its base diameter and use the measured
original-sprite queen-to-king base-width ratio (132/139). This implies a queen
height/base-diameter ratio of 2.1793. The evaluated model measures 2.1799.
That translation depends on the king model and the assumption that the sprites
share a render scale; it is not an independently measured physical height.

The model uses a continuous eight-point crown and turned body. A bounded
projected-ring fit weighted the original black Lichess sprite 70% and the
selected generated reference 30%, followed by actual Blender renders. At the
saved camera, silhouette intersection-over-union improved from 93.38% to
97.90% against the original and from 93.17% to 97.91% against the selected
reference. These scores measure the outline only, using a brightness threshold
for the dark references. They do not establish a perfect fit of the interior
contours, wood, lighting, or hidden surfaces. The collars, finial, and lighting
still have visible differences from the selected image.

The Blender file contains an editable, packed generated wood albedo and a
procedural component with studio lights. The viewer embeds the same image and
uses a real-time triplanar approximation of the Blender material and lights;
its shading will not be pixel-identical to Cycles. The texture's generator,
reference, and full prompt are recorded in `assets/queen/walnut-albedo-generation.json`.
The photo itself is not projected onto the geometry.

The previous canonical model and all 39 inputs of the earlier projection
study are archived in `history/queen-before-54-finish`. The existing projection
pages still show those historical alternatives, not the new current queen.
Their build and validation scripts use the archived baseline.

Rebuild from the repository root with Blender, Python with NumPy and Pillow,
and Node.js:

```sh
python scripts/queen/fit_54_finish.py
blender -b --python scripts/queen/build_finished_queen.py
blender -b --python scripts/queen/validate_finished_queen.py
blender -b --python scripts/queen/export_viewer_mesh.py
blender -b --python scripts/queen/inspect_viewer_camera.py
python scripts/queen/build_viewer.py
python scripts/queen/overlay_qa.py --reference-mask max-channel
python scripts/queen/compare_finished_queen.py
node scripts/queen/check_viewer_camera.cjs
node scripts/queen/check_review_reference.cjs
python scripts/queen/check_projection_variants.py
python scripts/check_site.py
```

The runtime checks execute the viewer code with a simulated DOM and WebGL
interface; they do not replace a native browser GPU inspection.
