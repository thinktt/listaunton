# Bishop iteration 008 — rejected pigment and base-reflection experiments

Date: 2026-11-05. Starting and retained model: checkpoint 007, commit
`9b87e11`. **No new model is accepted in this iteration.** The main review
page continues to show that validated checkpoint. The bishop mission remains
active and incomplete.

The original white Lichess bishop remains authoritative. Ungraded white
candidate 3 supplies detail; the fixed camera remains orthographic at 54°.
Reference pixels, source registration, side-gallery defaults and other pieces
are unchanged. `history/bishop-mission-007` preserves the starting model and
assets for reproducible isolated experiments.

## Material examination

The rear view still shows a conspicuous patch where reference-derived pigment
meets inferred wood. Four diagnostic renders of trial 058 isolate its cause:
the patch remains in a pigment-only emission diagnostic, survives removing
bump, and disappears with constant pigment and no bump. These are diagnostic
views, not replacement beauty renders. They establish that the patch is
principally embedded in pigment, rather than being caused by the geometry or
surface relief alone.

Five actual material trials were inspected from the fixed reference camera
and a rear camera:

| Trial | Change | Why rejected |
| --- | --- | --- |
| 058 | A continuous, softly constrained broad pigment field with bounded old fine grain | Front contrast weakens, while the old fine residual retains visible patch edges. |
| 059 | Continue the full color of a front strip around the back | Baked shadows become artificial dark horizontal bands. |
| 060 | Combine harmonic broad color with separately sampled fine grain | The broad bands and transition remain conspicuous. |
| 061 | Replace low-confidence wood with newly generated, evenly lit fine grain | Unseen grain is cleaner, but the color patch remains and an edge stripe becomes visible in the front view. |
| 062 | Combine stronger broad-color constraints with inferred fine grain | The rear transition softens somewhat, but the front loses important collar-groove and tonal contrast. |

The generated swatch is an **inferred texture source**, not recovered artwork.
It was created with the built-in image-generation tool, using the selected
bishop solely as a material reference. Its exact prompt, source hash and output
hash are recorded in
[`inferred-boxwood-source-01.json`](../../../assets/bishop/materials/inferred-boxwood-source-01.json).
The PNG is saved beside that record. It is not used by the accepted model.
The experiments use only its fine, zero-mean grain with a separately declared
base color; they do not assume the generated swatch is a calibrated albedo.

The [front montage](material-research/front-trials.png),
[rear montage](material-research/rear-trials.png), material-isolation images,
per-trial crops, hashes, parameters and measurements are preserved under
`material-research/`. Failed Blender models and atlases are not added to public
review controls.

## Lower-reflection examination

The accepted base highlight is too tall, too yellow and misplaced. Within
the declared base crop, the brightest blue-channel pixels have a centroid at
approximately (566.96, 974.37) in checkpoint 007, compared with (583.39, 994.75)
in the selected reference. This is a diagnostic for the bright core, not a
measurement of the original physical light.

Trial 063 changes the collar, socket and base light colors from strongly
yellow toward cream. Its hue is closer, but it also emphasizes the unwanted
socket line and incorrectly placed base reflection. Trial 064 moves the base
light using the actual evaluated surface and a measured, locally averaged
BSDF normal at the reference location. The glint remains overly tall and high.

Trial 065 aims farther down and flattens the emitter. It overshoots onto the
foot and introduces new spill. Trial 066 interpolates between the two measured
directions; it reduces the foot flash but loses the main reference glint.
None is an overall replacement for checkpoint 007.

The normal measurement is an unsaved emission diagnostic, with a three-pixel
averaging radius. The trial renders use the actual Principled material. Each
lighting trial checks that its control geometry, UVs, camera and material
state are unchanged. A separate reopened-scene audit of trial 066 checks the
declared light properties and preservation of the rest of the scene.

## Full trial scorecard

| Trial | Silhouette | Interior | Color | Texture | Lighting | Mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Retained 007 | 96.20 | 83 | 85 | 77 | 73 | 82.84 | Remains accepted |
| 058 | 96.20 | 83 | 75 | 72 | 68 | 78.84 | Reject |
| 059 | 96.20 | 83 | 84 | 72 | 73 | 81.64 | Reject |
| 060 | 96.20 | 83 | 84 | 73 | 73 | 81.84 | Reject |
| 061 | 96.20 | 83 | 84 | 74 | 73 | 82.04 | Reject |
| 062 | 96.20 | 83 | 80 | 75 | 70 | 80.84 | Reject |
| 063 | 96.20 | 83 | 85 | 77 | 73 | 82.84 | Reject; tradeoffs do not earn an increase |
| 064 | 96.20 | 83 | 85 | 77 | 73 | 82.84 | Reject; location/shape still inadequate |
| 065 | 96.20 | 83 | 85 | 77 | 68 | 81.84 | Reject; foot flash and spill |
| 066 | 96.20 | 83 | 85 | 77 | 71 | 82.44 | Reject; primary glint missing |

Only silhouette is measured. Other percentages are subjective assessments
using the unchanged mission rubric. They are not probabilities of fidelity.
The retained checkpoint's holistic fixed-view range stays **75–85%**. Trials
058 and 062 are approximately 70–80%; the other trials remain within a broad
75–85% range but have the specific regressions above.

All nine draft trials have selected-reference silhouette IoU 0.96197246,
original-white IoU 0.97876433 and original-black IoU 0.96753166. Their geometry
is unchanged; tiny alpha differences from the accepted 512-sample image arise
with rendering. Draft beauty images use 96 fixed samples, and rear material
diagnostics use 24. They were rejected on visible defects, without claiming
final convergence or interpreting their numerical RGB errors as fidelity.

## Preserved result and next step

The accepted model, atlas, mesh, camera, renders and both bishop pages remain
checkpoint 007. No experimental material or light is synchronized into the
owner's preview. The existing overlay, rotation and candidate tabs remain
available. This iteration changes research records and tools, not the public
model. Actual preservation checks are recorded in `checkpoint.json`.

The next supported hypothesis is that the base's broad, nearly uniform-normal
surface and its lower curvature transition shape the tall reflection. Inspect
the evaluated meridian and normal distribution against the reference's base
curvature before moving the light again. A small, isolated curvature trial
must preserve diameter, height, camera, upper anatomy and source registration,
and must pass both original and selected-reference comparisons. If lighting
spill remains a separate problem, receiver separation is a possible later
experiment; it has not been implemented here.

For pigment, the next attempt must jointly address the physical shading and
the tonal structure currently stored in the visible atlas. Repeating a
hidden-only fill, or retaining the same boundary as fine grain, is unsupported
by these results. Preserve checkpoint 007 while investigating.
