# Eleventh iteration: shaped bowl reflections

Start from tenth checkpoint 9df15a5, model SHA-256
6bbc7d1dbeffd54e846895eb1f9f3854092c8b57d4267fa49c621e7f67e74325.
The smaller finial, entire closed control, UVs, material, fixed 54-degree camera
and side-gallery proportions are preserved.

Knockout renders isolate the broad rear-bowl patch to three bowl reflectors.
Removing rim reflectors has little influence there; finial spots affect their
own glints. Diffuse-only rendering confirms a residual broad pigment pattern,
so lighting cannot solve the remaining grain discrepancy.

100-101 replace the broad bowl areas with two aimed spots but remain too broad.
102-103 narrow source and cone, locating the two glints but overexposing them.
104-105 undershoot their brightness; 106-107 improve intensity but still form
isolated blobs rather than the source's tapering arcs. 108-109 use eight small
linked physical emitters along two measured bright regions, improving shape
but undershooting intensity. All are rejected or superseded, never public
alternatives. The five-category scores for each are in scores.json; geometry,
color and grain assessments remain unchanged, with only lighting adjusted.

110 fits those eight powers through measured full-wood light responses and the
AgX display transform. Nine cropped 512-sample EXRs capture baseline and each
individual light at native image coordinates, with denoising/adaptive sampling
disabled. Other lights, world and material remain fixed during the solve.
The final decision uses a real full-resolution 128-sample BSDF render, not the
linear prediction. Its bowl-region RGB mean absolute error falls from 26.27 to
20.70 byte levels (21.2%); whole-crown error falls from 20.82 to 19.64. These
statistics support a localized visual gain, not a fidelity percentage.

Lighting receives 65 versus 64; form remains 81, color 80 and grain 77.
The glints remain too smooth, the stray upper-right bowl streak persists, and
the front inner-bowl crescent, collars/socket reflections, coarse grain and
base reflection still differ. Holistic assessment remains 75-80%. No claim of
completion or recovery of the original light rig is made.

Reproduction from repository root:

1. Blender: scripts/queen/focus_bowl_reflections.py -- --arc
2. Python with Pillow/NumPy: scripts/queen/prepare_light_fit.py --size 1254
   --directory build/queen-mission/bowl-arc-fit
3. Blender: scripts/queen/fit_bowl_arc_powers.py
4. Run the standard validation, publish/export, viewer and reference checks.

The archived tenth model is under history/queen-mission-010. The two diagnostic
scripts and generic narrow-beam trials reproduce the rejected exploratory
steps if necessary. New spot lights share the existing turned-body receiver;
finial isolation is preserved. Native browser GPU verification is not claimed.
Delivery and side-view checks pass. Side silhouettes are byte-identical; mean
wood RGB change is 0.394/255, with no visible side regression. Control vertices,
atlas UVs and topology are byte-identical to the tenth checkpoint. The receiver
validator confirms exact evaluated faces/UVs and the intended light links. Both
review interaction harnesses, viewer camera regression, source hashes, site links,
model tabs and protected projections pass. The 64-sample delivered outline is
97.9612% high-res / 97.9109% original; trial differences were sample/AA effects.
Working mean is 80.1922%, holistic 75-80%. The fitted lighting prediction differs
from the actual render by mean 5.34 byte levels in its crop; sampling/denoising
remain a diagnostic concern, and only actual renders justified acceptance.
