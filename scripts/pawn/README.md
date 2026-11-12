# Current pawn reconstruction

The accepted model uses a fixed 54-degree camera, a seated round head, a flatter sole and packed walnut pigment. Its measured finish combines roughness, polish strength and fine normal slopes, with a local matte/varnish mix beneath the head. See [the pawn mission log](../../docs/pawn-mission-log.md) for current scores and [checkpoint 015](../../docs/pawn-mission/iteration-015/README.md) for reproduction and scope validation. Open [the pawn review](../../pawn-review.html) for the fixed overlay, textured rotation and side comparison.

## Historical clay pipeline

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

The 57,984-triangle export has no nonmanifold edges and positive volume. Original-black silhouette overlap is 96.17%, original-white 95.90%, and selected candidate 93.22%; candidate shoulder/head proportions differ from the originals. Mean original-black contour discrepancy is about 0.99 source pixels. These scores measure visible outline, not unseen geometry or surface material.

The viewer starts with the original black reference, supports the selected enlargement, and switches to independent rotation while retaining the camera. Runtime checks verify overlay endpoints, camera reset, orbit/pan/zoom and no repeated-frame scale drift; maximum sampled camera discrepancy is below 0.000011 pixels. Native browser graphics have not been independently screenshot-tested. Wood finish and unseen underside remain later interpretation work.

## Seated head revision

Owner side-view feedback identified an exposed neck between the ball and collar. The ball is lowered by four original-image pixels into a broader inner seat. The outside collar and all lower-body meridian points are unchanged. The head and seat remain one closed continuous surface. `assets/pawn/side-seating.png` records the level view; `scripts/pawn/check_seating.py` checks preserved geometry and regenerates that view. The stronger seating reduces the original silhouette score from 98.07% to 96.17%; this is an intentional interpretation of the three-dimensional join, not a claim of a closer projected silhouette. The preceding shape is preserved in `history/pawn/04-before-seated-head`.
