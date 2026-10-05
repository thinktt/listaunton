# Side views at model-estimated relative sizes

All six transparent side views share a ground line and use height estimates from
our 3D models, with the king as 100%. The gallery keeps each image's aspect ratio.
On smaller screens the row scrolls horizontally at the same scale.

## Manual scale controls

Each piece has a 50–150% slider and a Reset button. 100% is its model-estimated
starting size. Scaling is uniform and anchored at the measured bottom-center of
the opaque foot, not at the PNG canvas edge. The anchor stays fixed horizontally
and vertically while dragging. The fixed viewing area reserves space for the
largest allowed sizes; the ground line does not move to accommodate an image.

Height labels compare with the king's current size and update when its slider
changes. Adjustments persist across tabs and, where browser storage is available,
refreshes. Reset affects only that piece. The reference-comparison candidates,
image files and model estimates remain unchanged.

## Piece order

Drag a piece sideways and drop it at the highlighted insertion point. Its card
moves horizontally only, preserving the common ground line and its current size.
The row scrolls when dragging near an edge. Left/right buttons provide precise
one-position moves; a focused piece also responds to arrow keys, Home and End.
Escape or pointer cancellation abandons an in-progress drag.

Order is saved separately from scale settings. Reset order restores the initial
lineup without resetting sizes. Reordering moves existing DOM nodes, preserving
their loaded images, controls and handlers. Normal slider use and the separate
full-size image links do not start a reorder.

## How the estimate works

The models were built with different arbitrary world-unit scales. Raw Blender
heights cannot be compared directly. Instead:

1. Measure each original white Lichess sprite's broadest lower-base width. White
   makes the boundary easier to distinguish from its shadow; it has the same
   geometry as the black piece. Horizontal diameters avoid vertical foreshortening
   and the clipped king cross.
2. Measure the model's height and round-base diameter. Use the lower quarter of
   the mesh for the diameter, excluding the knight's overhanging muzzle.
3. Compare each height/base ratio with the king's, then multiply by its original
   base-width ratio to the king. This puts the independently built models onto
   one estimated physical scale.
4. Set the king image to 430 px tall. Uniformly size every other cutout to its
   estimated height and align the opaque foot bottoms. Transparent margins do
   not affect the measurement.

All sources use the same assumed **54° elevation**: king, queen and rook use
their 54° projection variants; bishop, knight and pawn use their current models.
The existing models and review pages are unchanged.

| Piece | Original base width | Estimated height relative to king | Display height |
| --- | ---: | ---: | ---: |
| King | 139 px | 100.0% | 430.0 px |
| Queen | 132 px | 76.5% | 328.8 px |
| Rook | 118 px | 54.5% | 234.3 px |
| Bishop | 121 px | 80.2% | 344.7 px |
| Knight | 125 px | 61.9% | 266.0 px |
| Pawn | 103 px | 50.2% | 215.9 px |

These are **our current model estimates**, not recovered exact historical
dimensions. In particular, the current bishop estimate is taller than the
queen's. The gallery shows that discrepancy rather than imposing a conventional
height order. The knight is less firmly tied to its original overhead silhouette:
its current geometry prioritizes the approved generated side guide.

The generated side images and models do not have identical proportions. Matching
the estimated heights with uniform image scaling means their displayed base widths
will not all match the originals exactly. No cutout is stretched to force both.

The previous gallery used only base widths. A rook height check replaced that
method for the rook, and the user's follow-up extended model-estimated sizing to
the entire set. The former base-only heights and correction factors remain in the
measurement report for comparison.

Original width thresholds are repeated at five levels to expose the few-pixel
boundary uncertainty. `assets/side-views/scale.json` records the exact model and
camera sources, mesh hashes, measured dimensions, formula results and display
placements. Text-source hashes normalize CRLF to LF for Windows/WSL portability;
PNG and mesh-binary hashes are exact.

## Background removal

The built-in image generation tool edited each `side-01.png` with transparency
requested. Results are separate `side-01-cutout.png` files with real alpha;
their original opaque guides remain alongside them and are linked as **Before
removal**. AI extraction also altered some surface grain and framing, so these
are not pixel-identical alpha masks of the guides. The guides and original
generation records are retained for modeling and provenance.

Exact extraction prompts and input/output SHA-256 hashes are in each piece's
`assets/<piece>/concepts/side-01-cutout-generation.json`. The gallery inventory is
`assets/side-views/manifest.json`. Reproducible source measurements, alpha bounds,
threshold sensitivity, scale factors and placements are in
`assets/side-views/scale.json`.

Rebuild with Python plus Pillow and NumPy:

```sh
python scripts/measure_side_views.py
python scripts/build_set_comparison.py
node scripts/check_set.cjs set-comparison.html
python scripts/check_site.py
```

The last two scripts also check that references still match their hashes and
that changing tabs preserves the user's original comparison choices.
