# King checkpoint 013 — upper collar curve and reflections

Accepted **151-upper-right-placement**, independently rebuilt as **152** from
checkpoint 012. The upper collar has a gentler upper curve and better placed
reflections. The fixed 54-degree camera, overall proportions and v6 wood material
remain unchanged. The full visual-match mission is active and incomplete.

## What improved, and what did not

At enlarged scale, the old upper collar produced two thin reflected bands where
the reference has a broader patch. Simply increasing the existing lights made
that defect more conspicuous. A diagnostic that removed material bump normals
still showed the double reflection, supporting a geometry-related explanation.

The first raised-curve test went too far: its left reflected ray was blocked by
the upper body. The gentler version keeps that ray clear. A subsequent right
light adjustment corrects its measured placement. The upper-collar foreground
RGB squared error changes from 644.83
to 468.39; the left-glint region changes
from 2309.97 to
584.19. These support the visible improvement,
but are not calibrated perceptual-match scores.

The pigment band, fine surface structure and exact reflection breadth still do
not match. Broad/brighter light trials 144–146 and 150 are rejected. The more
strongly raised curve 147 is also rejected. Trial 149 is superseded by 151's right
light placement. No rejected trial is exposed as the current model.

| Metric | Checkpoint 012 | Checkpoint 013 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8258% | 97.8258% |
| Interior form | 85% | 85% |
| Wood color | 82% | 82% |
| Grain / surface | 79% | 79% |
| Lighting / reflections | 67% | 69% |
| Equal-weight working mean | 82.1652% | 82.5652% |

Original-sprite overlap is 96.8464%. Only overlap is
measured; the other scores are visual judgments. The holistic assessment remains
75–85%. Full images, enlarged crops, neutral form, side/rear views and both
original sprite colors were examined. A matching exterior mask does not prove
the inner profile or unseen geometry is exact.

## Exact scope and reproduction

Only body-control heights **58, 59 and 60** change by **+0.010, +0.007 and +0.003**
model units. Every radius and every other control coordinate stays exact. The
middle-collar repair from checkpoint 012 is preserved. The two existing upper
area lights remain shadow-enabled, glossy-only and confined to the upper collar:

- Left: target pixel (474, 429), distance 0.8, power 12, size 0.24 × 0.10.
- Right: target pixel (560, 430), distance 0.8, power 8, size 0.24 × 0.10.

Their color remains (1, 0.73, 0.5). These are artistic settings, not recovered
historical lights. Material nodes, packed textures, topology, UVs, float
attributes, other lights and their shadow/link settings, camera, world and
physical bounds are validated against the archived checkpoint 012.

From the repository root:

```sh
blender --background --python-exit-code 1 --python scripts/king/refine_collar_turning.py -- docs/king-mission/iteration-013/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/render_fixed_diagnostics.py -- build/king-mission/152-upper-collar-reproduction/king.blend build/king-mission/152-upper-collar-reproduction --beauty-only
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/152-upper-collar-reproduction/king.blend build/king-mission/152-upper-collar-reproduction
```

`verify_collar_candidate.py` runs scoped validation, receiver regeneration,
export, saved-file inspection and independent reconstruction. Its required
inputs are the candidate variant, archived baseline, report directory and a new
reproduction variant; `--blender` selects an installed executable. It does not
replace the current model. Diagnostic scripts are `probe_collar_normals.py` and
`diagnose_upper_normals.py`; the latter's smooth images are never final materials.

## Validation and review

The independently rebuilt scene matches the candidate's geometry, material,
lights and camera; exported mesh bytes agree exactly. Both controls have positive
volume and no nonmanifold edges. They remain intersecting separate body/cross
components, not a Boolean-fused solid. All nine receivers regenerate correctly;
the collar section has no detected crossings. Fresh fixed renders and their
repeat agree within 1/255, with exact alpha. The alternate entry point differs by at most 45/255 in this check. The earlier execution-context sensitivity remains documented; this result does not establish its cause or a universal fix.

The standard sampling settings remain 128 adaptive samples with denoising.
The fixed beauty, neutral view, profile, side/rear renders and rotating mesh are
synchronized from the saved model. All 34
Windows preview files match the repository. Canonical Blender validation,
king/candidate interaction checks and site/model checks pass. Source hashes,
gallery sizing defaults, other pieces and historical projections are preserved.
The live in-app browser was reloaded and visually checked; localhost serves the
accepted model/render hashes. Full fixed-view framing is intact.

The whole-set test is not rerun here; checkpoint 012 records the existing knight
sizing metadata mismatch. It is not counted as a pass. Historical projection
checks passed at checkpoint 012 and their inputs remain untouched.

## Remaining work

The upper glints still need more natural breadth and fine breakup. Pigment bands,
grain scale/flow and surface finish remain imperfect. The cross seat and upper
rim, socket glint continuity and central color, broad base reflection and foot
texture also need work. Hidden wood and lighting remain inferred. No watcher or
subagent was started, and nothing was pushed or published.
