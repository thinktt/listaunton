# Side views at one relative scale

The six generated side views in the set page now have transparent backgrounds,
sit on a shared ground line, and use one scale anchored to the king. Smaller
screens scroll the same row sideways; they do not resize each piece separately.

## What determines the scale

Measure the broadest lower-base width of each original **white 300 × 300
Lichess sprite**. The white wood makes the boundary easier to separate from its
shadow; it represents the same geometry as the black piece. The horizontal
diameter of a round base avoids vertical foreshortening and does not depend on
recovering the clipped tip of the original king's cross.

| Piece | Original base width | Relative to king |
| --- | ---: | ---: |
| King | 139 px | 100.0% |
| Queen | 132 px | 95.0% |
| Rook | 118 px | 84.9% |
| Bishop | 121 px | 87.1% |
| Knight | 125 px | 89.9% |
| Pawn | 103 px | 74.1% |

Scale each cutout uniformly until its base diameter has that ratio to the king's
base. The king is displayed 430 px tall. Center each piece on its base axis and
align its opaque bottom with the shared ground line. Transparent margins are
excluded from the measurement; generated image framing cannot change the result.

This assumes the original sprites share an orthographic or weak-perspective
camera and render scale. It establishes **relative base scale**, not exact
historical heights or physical dimensions. The generated side images still
contain interpreted proportions. In particular, the rook and pawn end up almost
the same height when their bases are scaled this way. Their heights were not
stretched independently to force a conventional chess-set ranking.

The few-pixel edge uncertainty is recorded by repeating the original measurement
with five brightness thresholds. Measurements exclude dark cast shadows and use
the lower part of each sprite. Nothing is changed in the original Lichess images.

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
