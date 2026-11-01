# Fresh queen rebuilt with the imagined side view

The current queen's mesh was created from an empty Blender scene. Its profile
was drawn using the generated side view as an artistic guide: a full curved
stem, rounded socket and base, a short flaring crown body, and three stacked
rounded collars. The source side view is an imagination, not a measurement of
the original model.

The original black Lichess sprite is the deciding visual reference. The new
controls were fitted to its outline under the working assumption of an
orthographic camera 54° above the board. A second fit used an actual Blender
render; the camera received only a uniform scale and translation. The selected
high-resolution queen remains available as a secondary guide.

At this camera the new outline overlaps the original by **97.43%**, compared
with **97.90%** for the immediately preceding queen, under the same mask and
registration method. The earlier model's silhouette scores slightly better;
the new model aims for a more convincing side carving. Neither silhouette
score tests internal features, wood, lighting or the unseen geometry. The
new crown and its reflections still differ from the original.

The fresh model is 2.126 base diameters tall. Using the earlier uncertain
sprite-base-width normalization with the 54° king model gives an estimated
queen height of **81.3%** of the king, against the owner's saved display choice
of 83.4%. The shared set's side-view defaults were not changed. In a digital
set the queen can be scaled uniformly to the chosen relative height; that
would alter the inferred queen-to-king base-width relationship slightly.

The review page opens with the original Lichess image selected. Its **Side
comparison** tab aligns the side render with the imagined guide at the foot
using a single uniform scale and translation. It does not warp either shape;
extra space above the guide keeps the taller model visible. Select neutral or
wood and adjust opacity to see their differences. The preceding queen is
available as **Previous** on the main overlay, and its editable Blender file
is archived in `history/queen-before-scratch`.

To rebuild the accepted current controls and review data with Blender, Python
with NumPy/Pillow, and Node.js:

```sh
blender -b --python scripts/queen/build_scratch_queen.py
blender -b --python scripts/queen/validate_scratch_queen.py
blender -b --python scripts/queen/write_scratch_landmarks.py
blender -b --python scripts/queen/export_viewer_mesh.py
blender -b --python scripts/queen/inspect_viewer_camera.py
python scripts/queen/build_viewer.py
python scripts/queen/overlay_qa.py --reference-mask max-channel
python scripts/queen/compare_finished_queen.py
python scripts/queen/build_side_comparison.py
node scripts/queen/check_viewer_camera.cjs
node scripts/queen/check_review_reference.cjs
python scripts/queen/check_projection_variants.py
python scripts/check_site.py
```

The accepted fit is stored in `assets/queen/scratch-fit.json`. The exploratory
fitting scripts operate on rendered iterations and should not be run as a
single blind rebuild sequence. Viewer checks simulate DOM and WebGL calls;
they are not a native browser GPU inspection.
