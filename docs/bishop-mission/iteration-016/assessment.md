# Bishop iteration 016 — base finish studies rejected

Checkpoint **015 remains the accepted model**. None of this iteration's
experiments is promoted. The owner asked the project manager to have the
current workers finish their ongoing iteration and pause. This iteration is
complete; no further modeling or rendering batch is pending. The full mission
is incomplete and may resume only at the owner's direction.

## What the tests found

Three grain-dependent roughness fields barely change the base glint. They
leave its smooth, concentrated triangular shape and do not justify a material
change. The actual 512-sample crops preserve geometry, pigment and relief.

Broader base reflectors were tested on a temporary split of the exact existing
render surface. Positions, UVs, material slots and source attributes remain
exact; custom corner normals are checked within the established tolerance.
The partition-only control has effectively the same rendered appearance.
The first receiver band starts too low and still includes the foot shoulder.
Raising its lower boundary to z=.42 excludes that spill. Larger disks and
reduced power soften the glare, but none reproduces the reference pattern.
These are unsaved crop diagnostics, not accepted three-region model revisions.

Turning off the base reflector leaves the dark patch beneath its glint. A
pigment-only diagnostic confirms that much of the boundary is already in the
color map. Removing bump or using constant pigment distinguishes that defect
from the reflection itself. Emission images are diagnostic measurements only;
the model candidates use the real Principled BSDF.

Two local pigment repairs use actual black/white BSDF and pigment responses.
Unlike the older inverse, they treat clipping per color channel; a clipped
reference channel supplies a lower bound instead of discarding the other
channels. The correction is confined to a feathered patch on visible lower-base
surfaces, preserving alpha and every atlas texel outside that scope. The first
repair changes 24,516 texels; the second changes 24,572 out of 4,194,304.

Both saved scenes are reopened, their packed pixels agree exactly with the
trial atlas, and their full actual BSDF renders use 512 fixed samples. The
second repair gives the red channel's lower bound more weight and permits a
larger correction. Both reduce RGB error, but the yellow-green patch remains
visually wrong and the wood/glint structure does not match. They are rejected.
No independent full promotion audit was run after that visual rejection.

## Scores and measurements

| Full model | Silhouette | Interior | Color | Grain / finish | Lighting | Decision |
|---|---:|---:|---:|---:|---:|---|
| Accepted 015 | 96.11 | 84 | 86 | 78 | 77 | Retain |
| 132, local channel correction | 96.11 | 84 | 85 | 78 | 77 | Reject |
| 133, stronger clipped-channel correction | 96.11 | 84 | 85 | 78 | 77 | Reject |

Silhouette is measured overlap; the other ratings are subjective estimates.
The current working mean remains **84.22%**, with a holistic fixed-view range
of **75–85%**. The cropped roughness and lighting probes do not receive invented
whole-model scores. All five categories of the accepted model remain unchanged.

| Shared opaque foreground RGB MAE, /255 | Accepted 015 | Trial 132 | Trial 133 |
|---|---:|---:|---:|
| Whole piece | 5.9816 | 5.4556 | 5.3539 |
| Base | 9.0137 | 7.1793 | 6.8247 |
| Foot | 5.4929 | 5.4650 | 5.4647 |

Those losses do not establish perceptual fidelity. In particular, bringing a
broad patch closer numerically does not recover its natural hue, contrast or
grain. The original-white and original-black silhouette overlaps remain
97.786% and 96.661%; selected-reference overlap remains 96.109%. No registration
or reference pixels changed. The camera remains fixed at 54 degrees.

## Preserved result and remaining defects

The public Blender model, atlas, fixed render, rotating mesh, side views and
review pages remain checkpoint 015. Its previous saved-scene and interaction
checks remain applicable to those byte-identical artifacts. This iteration
verifies their hashes in the stage, canonical repository and local preview;
the delivery record is `checkpoint.json`. Checkpoint 015 is also archived for
reproducing these experiments. Rejected candidates are evidence only.

Unresolved defects include the base/button reflection shapes, pigment near
highlights, fine grain, the upper-head material boundary, inferred rear grain,
collar/socket arcs and slit-edge finish. The experiments support the owner's
assessment of a plateau; the full match is not achieved. If the owner resumes
work, pigment and illumination separation around clipped highlights needs a
different approach before adding more reflector complexity.

No quota monitoring, subagents, publication or push was performed. Browser
inspection remains unavailable under the earlier local-URL policy restriction;
no workaround was attempted. Actual Blender renders and recorded artifact
checks are the evidence used here.
