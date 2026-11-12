# Bishop iteration 015 — closer lower-body pigment

The goal remains active. The owner explicitly confirmed that no pause is
requested. Trial 125 is the accepted material, with the saved model, export
and synchronized-page checks recorded in `checkpoint.json`.
Checkpoint 013 remains archived. The camera stays at 54 degrees, original white
is authoritative, and ungraded white candidate 3 remains the detail reference.

## Findings and decisions

Height-dependent average color makes the back more continuous, but loses the
reference's contrast. Adding a smooth angular variation worsens the collars
and foot. These are rejected as complete materials; the smooth field is useful
only as an inferred continuation where the reference supplies no observation.

Actual BSDF response measurements let the next trials estimate visible pigment
without using the older projection-confidence boundary. The method subtracts
the measured black-material response, applies bounded local color feedback,
and projects it through the actual surface-position and visibility fields.
Uncertain clipping, reflections, weak response and edges reduce the correction.
This is approximate pigment estimation under inferred lighting, not recovery
of a fully unlit source texture.

The first versions replace uncertain reflective areas too aggressively with
inferred grain. A second response iteration does not fix the resulting washed
out rings. Preserving the current pigment in those areas helps, but a remaining
log-detail clamp still truncates about **17%** of reliably observed texels.
Removing that clamp restores the collar and foot contrast. Trial 124 improves
the lower body but regresses on the upper head, so its whole-body replacement
is rejected. Trial 125 restricts it to the turned lower body with a smooth
height transition, retaining the better upper head and button pixels exactly.

The final scene was saved, reopened and rendered at 512 fixed samples. The
full image and enlarged head, stem/socket and base comparisons show a modest
improvement in wood tone. Actual side/rear renders show a less abrupt lower-body
color patch. The grain still changes character toward the back, the stem has
an inherited tonal boundary, and the preserved head still has a visible patch.
This is partial progress, not a seamless or physically recovered texture.

| Result | Silhouette | Interior | Color | Grain / finish | Lighting | Decision |
|---|---:|---:|---:|---:|---:|---|
| Accepted 013 | 96.11 | 84 | 85 | 77 | 77 | Archived |
| 116, height color | 96.11 | 84 | 77 | 75 | 73 | Reject |
| 117, half blend | 96.11 | 84 | 82 | 76 | 75 | Reject |
| 118, angular color | 96.11 | 84 | 73 | 73 | 71 | Reject as a complete material |
| 120, visible inference | 96.11 | 84 | 83 | 76 | 75 | Reject |
| 122, second response | 96.11 | 84 | 83 | 76 | 75 | Reject |
| 123, preserve uncertain pigment | 96.11 | 84 | 84 | 77 | 76 | Reject |
| 124, retain visible contrast | 96.11 | 84 | 85 | 78 | 77 | Reject whole-body version |
| 125, retain better head | 96.11 | 84 | 86 | 78 | 77 | Accept after final checks |

Silhouette is measured overlap; the other percentages are visual estimates.
The accepted working mean is **84.22%**, with a holistic fixed-view range of
**75–85%**. Original-white overlap remains **97.786%**, original black
**96.661%**, and selected-reference overlap **96.109%**. The unchanged outline
does not establish the correctness of the slit or hidden shape.

| Foreground RGB MAE, /255 | Accepted 013 | Trial 125 |
|---|---:|---:|
| Whole shared opaque foreground | 7.1865 | 5.9816 |
| Collars | 6.0016 | 5.2220 |
| Stem | 2.2533 | 1.8091 |
| Socket | 5.7880 | 4.2309 |
| Base | 11.0853 | 9.0137 |
| Foot | 6.5423 | 5.4929 |

The numerical gain supports the visible color improvement; it is not a fidelity
percentage. The base/button glints remain too smooth and concentrated, the
socket band remains too regular, collar reflections and slit-edge finish still
differ, and fine grain is softer than the reference. The lighting score is
unchanged. Rejected 256-sample studies have different denoising behavior; the
accepted before/after comparison uses 512 samples for both.

## Preservation and next work

Only the packed pigment atlas changes. The actual scene audit checks the
unchanged controls, slit cutter, UVs, relief graph, coat, lamps, receiver
surfaces, world, display path and camera. Saved atlas pixels match disk exactly.
Historical atlas changes are now checked as a chain back to the strict receiver
audit. Each archived atlas is resolved by its declared hash; no earlier material
change is silently ignored. Export and page verification are recorded separately.

Next preserve this color result while investigating fine grain and spatial
polish variation. Broad tone and small surface variations need separate
treatment; repeating the earlier stronger-bump or flat-color trials is unlikely
to help. Any new roughness or grain field must be judged in actual fixed and
rotated BSDF views. The full mission is incomplete. No quota monitoring,
subagents, publication or push was performed.
