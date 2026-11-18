# Pawn side checkpoint 002

The pawn now has continuous walnut in the inferred parts of the ball, neck,
base and rear. The artificial bright stripe across the upper stem is removed.
Only radial control 10 changes, from 0.7389464 to 0.775, easing the base
undercut while retaining the foot lip. Every height, all other control
coordinates, UVs, both lighting rigs and the fixed 54-degree camera remain
unchanged. Both saved scenes use the same editable object and material.

This is an accepted improvement, not a finished pawn. The broad socket and
heavy collar still weaken the profile. The front retains pale patches and
some transitions between observed and inferred grain; the rear is cleaner.
The side-quality goal remains active.

## Side assessment

These scores are subjective aesthetic judgments using the unchanged rubric.
They are not a percentage of historically recovered geometry or image pixels.

| Criterion | Previous | Current | Weight |
| --- | ---: | ---: | ---: |
| Profile and proportions | 68 | 70 | 30% |
| Turned details | 60 | 64 | 15% |
| Wood continuity | 48 | 70 | 20% |
| Surface finish | 62 | 70 | 15% |
| Lighting and form | 82 | 82 | 15% |
| Seating and presentation | 85 | 85 | 5% |
| Weighted quality | 64.85 | **71.65** | 100% |

The saved side studio is unchanged. Lighting receives no new credit for
the material improvement. The target remains at least 90 overall, with no
category below 85. Inspect [before/after](side-before-after.png),
[four azimuths](orbit-sheet.png), and [reference comparison](comparison.png).

## Reference-view tradeoff

The original black sprite's native-size RGB error is effectively unchanged:
16.6709 to 16.6692 on the 0–255 scale. Its silhouette overlap is 98.50%;
the selected generated reference overlap is 96.81%. Registration stays fixed.
The small overlap changes are at sampling/alpha boundaries, not a new fit.

Against the selected high-resolution reference, regional RGB errors rise
from 2.740 / 2.306 / 2.706 to 3.197 / 3.408 / 3.356 for head / collar-stem /
base-foot. This modest loss of fitted texture detail is accepted for the
substantial improvement outside the source view. It is not a pixel-identical
replacement. The reference's three head glints and foot highlight remain
recognizable and closely placed. Native glint-center errors remain approximately
0.74, 0.58 and 0.91 original pixels.

## Material and geometry

A generated, unlit walnut tile supplies inferred grain through three blended
object-space projections. The observed texture is retained where the saved
camera/depth measurement is reliable, with a smooth transition. A bounded
height band removes the painted neck stripe. Color, relief, varnish and fine
slopes use the same completion weight. The results are ordinary static UV
maps rendered by the existing real BSDF and lights. There is no camera-dependent
material switch, emission-based beauty image or composited reference.

The [tile generation record](../../../assets/pawn/material-studies/continuous-walnut-generation.json)
contains the exact prompt and source/output hashes. It used the built-in
`image_gen.imagegen` tool. This texture is an artistic interpretation, not
evidence about the original artwork. The earlier
[generated unlit pawn](../../../assets/pawn/material-studies/albedo-01-generation.json)
was tested only for broad color and rejected as ineffective at fixing seams.
It is not the source of the accepted maps.

The model has 57,984 triangles, one closed connected component, no nonmanifold
edges, positive volume, and no meridian crossings. Overall height and diameter
are preserved. All packed references are byte-identical to their source files.
The previous checkpoint is in `history/pawn-side-quality-001`.

## Reproduction

Run from the repository root in the configured Blender/Python environment:

```sh
blender --background --python-exit-code 1 --python scripts/pawn/capture_side_source.py -- docs/pawn-side-quality/iteration-002/capture-geometry.json
python scripts/pawn/bake_continuous_wood.py docs/pawn-side-quality/iteration-002/material-bake.json
blender --background --python-exit-code 1 --python scripts/pawn/accept_side_material.py -- docs/pawn-side-quality/iteration-002/reproduction.json
blender --background --python-exit-code 1 --python scripts/pawn/validate.py -- .
python scripts/pawn/compare.py
python scripts/pawn/contact_sheet.py
python scripts/pawn/build_side_comparison.py
python scripts/pawn/build_viewer.py
python scripts/build_candidate_pages.py --piece pawn
python scripts/build_set_comparison.py
```

The material bake writes scratch maps under `build/pawn-side-quality/016-retained-reference/maps`.
Its result records match the committed `pawn-walnut-v12`, `pawn-walnut-relief-v3`,
`pawn-varnish-v10` and `pawn-fine-slopes-v11` PNGs in `assets/pawn`. The accepted
builder uses those committed, hash-checked maps. The depth capture is freshly
measured from checkpoint 001, rather than requiring an undocumented old cache.
Blender 5.2.2, NumPy 2.3.5 and Pillow 13.0.0 were used.

## Rejected alternatives and remaining work

- Broad color removal left the grain-direction seams intact.
- Reflected atlas extension introduced tiled-looking joins and copied glints.
- Full replacement with continuous wood lost too much original grain and finish.
- Broader material blending weakened the high-resolution match unnecessarily.
- Moving both groove controls weakened the foot highlight. Only control 10
  is retained in the accepted shape.
- The narrower socket moved its highlight; it is not included.

The study configurations, comparison images and measured errors are under
`studies/`. Next work should refine the collar/socket shape while retaining
their observed reflection arcs, and soften the remaining front grain boundaries.
The 90-degree and 270-degree views still expose those boundaries; do not rate
the material as finished based on the clean rear alone.

The saved/reopened model and direct Cycles renders were checked. Browser
interaction checks use mocked WebGL; native browser GPU rendering was not
retested after the earlier local-file URL-policy rejection.

## Site checks

Pawn viewer, all-piece model site, lineup, height modes, board comparison,
proportion warping and candidate controls pass. Whole-set presentation checks
also pass. The full whole-set check still fails on the pre-existing knight
sizing-provenance hash; knight sources and recorded sizing are unchanged in
Git content (text line endings normalized when comparing with HEAD). That
unrelated provenance was not rewritten. Full outputs and the distinction
are in [site-checks.json](site-checks.json).
