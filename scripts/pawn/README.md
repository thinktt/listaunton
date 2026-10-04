# Pawn reconstruction

The original black and white Lichess sprites govern the shape; selected black candidate 2 supports detail interpretation. All three source PNGs are unchanged and packed into the editable scene.

One connected, closed lathe surface forms the round head, shallow saucer collar, curved stem, shoulder bead, flared base and two broad foot rolls. The saved orthographic camera is 54°. Four geometry passes refined the head, collar height, shoulder band and foot. Prior passes are under `history/pawn/`; `assets/pawn/comparison-contact-sheet.png` compares both originals, selected reference and final render.

## Rebuild

Run from the repository root with Blender, ordinary Python with Pillow/NumPy, and Node:

```sh
blender --background --python scripts/pawn/build_pawn.py
python scripts/pawn/compare.py
blender --background --python scripts/pawn/validate.py -- "$PWD"
python scripts/pawn/build_viewer.py
node scripts/pawn/check_viewer.cjs
python scripts/build_candidate_pages.py
python scripts/check_model_site.py
```

The 58,752-triangle export has no nonmanifold edges and positive volume. Original-black silhouette overlap is 98.07%, original-white 97.86%, and selected candidate 95.11%; candidate shoulder/head proportions differ from the originals. Mean original-black contour discrepancy is about 0.56 source pixels. These scores measure visible outline, not unseen geometry or surface material.

The viewer starts with the original black reference, supports the selected enlargement, and switches to independent rotation while retaining the camera. Runtime checks verify overlay endpoints, camera reset, orbit/pan/zoom and no repeated-frame scale drift; maximum sampled camera discrepancy is below 0.000011 pixels. Native browser graphics have not been independently screenshot-tested. Wood finish and unseen underside remain later interpretation work.
