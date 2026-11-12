# Iteration 008 — socket and collar diagnostic; paused

The owner requested a pause after finishing current work on 2026-11-12.
Diagnostic 096 is complete and saved. **Checkpoint 007 remains the accepted
model and the model displayed by the review page.** No geometry, material,
light, camera, receiver or review-page changes were made in this diagnostic.
The mission is incomplete. Resume only on the owner's direction.

## Findings

- The broad `Front varnish` source produces most of the socket's doubled,
  pale, central/right streak. The reference has smaller, warmer glints with
  different separation and a fine inner seam.
- `Upper varnish` contributes little to the socket but makes prominent right
  collar crescents. Both broad sources produce regular, parallel collar
  streaks; the reference has less regular, warmer separated patches.
- Removing both sources exposes gray/brown bands and orange pigment patches.
  The diffuse pigment still contains source shading. Lighting alone may not
  repair all of these differences.
- These are illumination-isolation diagnostics, not candidate final renders.
  No visual improvement is accepted and no score increase is claimed.

The socket and collar contact sheets compare the selected reference, accepted
007 render, both broad sources disabled, front source disabled, and each source
in isolation. Source/reference pixels are unchanged; only analysis crops are
resized for viewing.

![Socket lighting diagnostic](socket-comparison.png)

![Collar lighting diagnostic](collar-comparison.png)

## Evidence and reproduction

`diagnostic.json` records source SHA, the full control profile, reflection-ray
probes and accepted light powers. Five PNGs preserve the isolation renders.
The render region is x=300–710, y=320–845 on the unchanged 1254-pixel canvas;
pixels outside the region are transparent. Cycles used 128 samples and denoising.

Run Blender from the repository with its current Python dependencies:

```text
blender --background --python-exit-code 1 --python scripts/king/diagnose_upper_reflections.py -- history/king-mission-007/king-rebuilt.blend build/king-mission/096-upper-reflection-diagnostic-reproduced
```

The script opens the source read-only, changes light powers only in memory,
renders the diagnostic views, verifies the source hash, and does not save a
replacement Blender scene. `diagnostic-render.log` records successful completion.

`socket-feature-locations.json` contains exploratory reference features from
the x=370–630, y=710–800 crop: Gaussian blur radius 2, blue channel >70,
four-connected components larger than five pixels, centroid weighted by
blue-minus-70. Bounds use inclusive maxima. This threshold is a locator, not
a definitive segmentation of highlights or a fit score. Two lower glint
centroids are approximately (464.6, 769.3) and (554.6, 772.3); three upper
components are also recorded. Treat these only as starting probes.

`pause-checkpoint.json` verifies that current model/render/pigment/references
retain their accepted hashes, the protected pipeline and review files have no
changes from the accepted commit, and all nine archived 007 assets match the
current accepted files. Script syntax and render completion pass. The existing
king review is unchanged, so its checkpoint-007 validation still describes it;
no new full site validation or native browser inspection is claimed.

## Scores retained from 007

| Category | Score |
| --- | ---: |
| High-resolution silhouette IoU (measured at 007) | 97.8171% |
| Interior form (subjective) | 84% |
| Wood color (subjective) | 82% |
| Grain / surface (subjective) | 79% |
| Lighting / reflections (subjective) | 62% |
| Equal-weight working mean | 80.9634% |

Original IoU remains 96.8335%; the holistic estimate remains 74–83%. These are
carried-forward scores, not new measurements of the intentionally incomplete
isolation renders. The documented whole-set check's pre-existing knight sizing
metadata mismatch remains outside this king task.

## Pending work

After the owner resumes, test a separate socket receiver before changing
geometry. Candidate split: current upper-body interval 19.8–28 becomes socket,
with upper-body continuing above ring 28; retain the four existing regions'
coverage during migration. Exclude the socket from the two broad varnish
sources and test warmer targeted reflections. Validate receiver regeneration,
normals, UVs and light routes; do not weaken the current checks. This receiver
split and lighting experiment have **not** been implemented. Preserve the
accepted foot and keep collars for a separate later study if necessary.
