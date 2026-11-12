# King checkpoint 010 — inner socket reflection

Accepted trial **113-socket-fitted-seam**. Two narrow, warm area reflections
restore more of the inner socket line without flooding the neighboring stem.
This is a modest lighting improvement, not a finished king. The goal is active.
Checkpoint 009 remains archived in `history/king-mission-009`.

## What examination showed

The missing bright line and the orange center patch have different causes.
Diagnostic 105 renders accepted shading, diffuse-only material, and pigment
under AgX and Standard views. The center band remains in pigment. Sampling
the reference shows that some neighboring brown pixels are already close;
blanket warming would damage them. The central patch is too dark and orange,
while several pixels along the inner lip lack a reflection.

The emission/diffuse diagnostic crops are investigative evidence only. The
accepted scene retains its real BSDF, original v6 pigment, relief and finish.
No source image was modified, and no image was composited into the final render.

## Trial decisions and all five scores

| Trial | Decision | Outline IoU | Interior | Color | Grain / surface | Lighting |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 106 broad center pigment grade | Rejected: shifts already-close colors | 97.8174 | 84 | 81 | 79 | 63 |
| 107 fitted pigment gain | Not accepted: insufficient clear gain | 97.8174 | 84 | 82 | 79 | 63 |
| 108 narrow center pigment grade | Deferred: useful local correction only | 97.8174 | 84 | 82 | 79 | 63 |
| 109 unrestricted seam reflectors | Rejected: broad bright stem patches | 97.8174 | 84 | 82 | 79 | 58 |
| 110 local seam polish | Rejected: adjacent spill remains | 97.8174 | 84 | 82 | 79 | 62 |
| 111 isolated seam reflection | Superseded by fitted powers | 97.8174 | 84 | 82 | 79 | 64 |
| 112 partition without new lights | Preservation diagnostic | 97.8174 | 84 | 82 | 79 | 63 |
| **113 fitted seam reflection** | **Accepted** | **97.8174** | **84** | **82** | **79** | **64** |

Only outline IoU is measured; other percentages are visual judgments using the
unchanged rubric. Original-sprite IoU is **96.8338%**. The equal-weight working
mean is **81.3635%**, versus 81.1635% at 009; holistic estimate remains **74–83%**.
No geometry gain is claimed. See `scores.json` for exact values and decisions.

The inner-seam RGB error falls from 600.289 to 346.040 (about 42%); the broader
socket crop falls from 251.469 to 201.006 (about 20%). The quiet center remains
essentially unchanged. These fixed-region squared-error values are diagnostic,
not visual-match percentages. Head, collars, stem and base remain unchanged
apart from minimal render sampling variation. `regional-measurements.json`
records masks, regions and values.

Full and enlarged comparisons, both original colors, neutral, side and rear
renders were inspected. The line is improved but still not a continuous exact
match. The outer socket glints remain patchy, and the central orange pigment
patch remains. The other visible defects listed below are not concealed by the
small numerical gain.

## Actual scene change

The closed body and separate closed cross, all positions, UVs, float attributes,
materials, packed images, camera and world remain exact from checkpoint 009.
The camera remains orthographic at **54 degrees above the board**. The export
remains 70,364 triangles with the same physical bounds and exact mesh bytes.

One sixth exact body light receiver isolates evaluated faces whose mean
`King profile ring` lies in **[26.55, 27.25)**. It is an illumination partition,
not a cut in the editable geometry. The original socket lights now cover both
socket pieces, preserving their previous coverage. Two new glossy-only AREA
lights link only to the inner-seam receiver. Both cast shadows and use real
material reflection; all existing light settings remain exact.

| New source | Target pixel | Rectangle | Distance | Power | RGB |
| --- | --- | --- | ---: | ---: | --- |
| Socket seam left | 465, 748 | 0.20 × 0.012 | 0.28 | 0.6773523868 | 1, .78, .62 |
| Socket seam right | 550, 744 | 0.20 × 0.012 | 0.28 | 0.5790320400 | 1, .78, .62 |

The acceptance does **not** include pigment corrections 106–108 or the local
polish from 110. Their parameters and rendered evidence are retained for study.
Any future procedural pigment correction must also be represented in the
interactive viewer or baked into the export; it cannot silently diverge there.

## Reproduction and validation

From the project root, using Blender 5.2.2 and the existing Python dependencies:

```sh
blender --background --python-exit-code 1 --python scripts/king/socket_seam_trial.py -- docs/king-mission/iteration-010/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/114-seam-checkpoint-reproduction/king.blend build/king-mission/114-seam-checkpoint-reproduction
```

The reproduction begins from archived checkpoint 009, not a temporary fitted
scene. `reproduction.json` records final fitted powers. Configs 106–113 retain
the experimental sequence; intermediate source hashes can differ on rebuilding
Blender files and must be verified, not blindly bypassed. The accepted builder
does not require the rejected pigment/polish trials.

- Saved/reopened and independently reproduced beauty agree within **1/255**,
  with identical alpha. Exact mesh bytes, camera JSON and physical bounds match.
- The receiver split by itself agrees with 009 within 1/255, with identical alpha.
- Closed geometry, UVs, every float attribute, material/packed images and old
  lights pass scope checks. Both closed components have positive signed volume
  and no nonmanifold edges; the components are intersecting, not Boolean-fused.
- Exact receiver faces, UVs, attributes, normals, material links and light
  routes pass. Regeneration passes for the new six-receiver and older
  five-receiver scenes.
- Canonical king validation, king/candidate interaction checks, site/model
  checks and historical projection checks pass. The actual-page DOM/WebGL
  harness passes for both repository and local preview. Native browser
  screenshot inspection is not claimed.
- All **34** king preview files are synchronized and hash-verified. Fixed,
  neutral, side/rear renders and the interactive geometry use this saved model;
  the browser's lighting remains an approximation.
- The whole-set check stops at its known **knight sizing metadata mismatch**.
  Its three relevant files are unchanged since `68f1041`. Assertions after
  that failure did not execute. See `whole-set-limitation.json`; this is not
  reported as a whole-set pass.

Hashes are in `checkpoint.json` and `source-hashes.json`; logs and exact checks
are alongside this file. Neither the source images nor shared gallery defaults
were changed. Other piece work and historical projection studies are preserved.

## Remaining discrepancies / next step

1. Upper collars still carry overly regular pale crescents. Diagnose their
   individual source contributions, preserving the accepted socket and foot.
2. Socket outer glints remain patchy and the inner line is not exact. The small
   center pigment patch still needs a restrained, viewer-compatible correction.
3. Base glints are too small/localized; the foot reflection is too smooth.
4. Cross seating, collar transitions and cavity contrast remain imperfect.
5. Grain relief/finish is uneven, with inferred hidden wood and projected
   texture limitations visible outside the reference angle.

No watchers or subagents were started. The full visual-match mission remains
incomplete; this checkpoint is not a completion claim.
