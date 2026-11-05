# Fifteenth queen iteration: collar reflections and interreflection

Accepted 2026-11-05, starting checkpoint d1dad12.
Starting model: eac23f7c9bbead43a22ea621f2a05a0604eeeebcc13a131e53ffabaca6302223.
Accepted trial: 145-direct-glossy-collars. Delivered model: 8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0.
Reference: bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a.

## Findings and decisions

Native isolated-light and material diagnostics separated the collar lighting
from pigment and relief. Several reflectors aimed elsewhere illuminated the
collars. Removing those contributions alone (140) made the stack too dark;
23 targeted emitters with uniform power (141) overexposed neighboring edges.
Fitting only the new emitters (142) was also rejected. Ten regional copies
of the accepted lights preserve a useful illumination basis (143 is a fixture,
not a scored candidate). Their powers and the new emitters were fitted through
AgX using measured native BSDF responses at 512 samples (144).

The fit lowered numerical error but strengthened a stripe across the crown
body. A diagnostic varying only glossy bounce depth established that this
stripe is secondary interreflection from the lit collars. Trial 145 retains
the actual wood BSDF and direct diffuse/glossy lighting, four diffuse bounces,
and sets secondary glossy bounces to zero. This is an artistic rendering
approximation, not a claim to recover the historical renderer. Full fixed,
original-reference and side comparisons support acceptance. The material
and its v8 pigment/relief remain unchanged.

The actual collar-crop weighted error falls 14.61%. This is a local
supporting measurement, not a whole-piece fidelity score. Rejected 144 also
lowered fitting error, illustrating why the visual review governs acceptance.

## Scores

Outline 97.9612% measured IoU, form 82, color 84,
grain 79, lighting 72; equal mean 82.9922%, holistic 79-84%.
Original IoU 97.9109%.
Other scores are subjective and unchanged; lighting rises from 70 to 72 for
the cleaner crown body and improved collar glints. See scores.json for every
rendered candidate. Do not mistake the measured silhouette for total fidelity.

## Preservation and validation

The closed editable geometry, UVs, atlas, camera, height/base ratio, compact
finial and side-gallery presets are unchanged. Four exact evaluated receivers
are now turned-body, stem-socket, collars and finial. Collars contain faces
whose centers have 2.78 <= z < 3.34. Face/UV records and custom smooth normals
are checked against the same closed control, which remains the exported mesh.
Run partition(..., socket_band=True, collar_band=True) after later mesh edits.

Source 14 is archived in history/queen-mission-014. Geometry, saved/reopened
render and independent reconstruction checks are attached. The strict one-byte
bound failed on sparse sharp glints; repeated native 64-sample renders have
opaque-pixel 99.9th-percentile differences of 1-2 bytes and rare maxima up
to 49 bytes, with identical alpha. These are sampling tolerances, not a claim
of bit-exact reproduction or perfect visual fidelity. The delivered
fixed/side renders, viewer and local page are regenerated and checked together;
no native browser GPU inspection is claimed. See delivered checks and sync log.

## Reproduction

Run Blender with scripts/queen/rebuild_collar_checkpoint.py and the default
iteration-015/reproduction.json. It rebuilds from tracked archive 14 and recorded
lights, retaining the packed v8 material, and produces private trial 146.
To reproduce the experimental sequence, build_collar_reflections.py takes
--source history/queen-mission-014/queen-rebuilt.blend; then run
fit_collar_crescents.py, retain_collar_fill.py, fit_retained_collar.py and
direct_glossy_collar_trial.py in that order. For the repeatability check, use render_saved_trial.py on trial 145 twice,
preserving the first result as wood-first-reopen.png; after reconstruction 146,
run scripts/queen/check_collar_reproduction.py with Python, NumPy and Pillow.
Diagnostic scripts do not alter their sources. Source reference pixels are never edited.

## Remaining discrepancies and next step

The reference's middle-collar front-left crescent is still brighter and more
continuous. Upper glints remain fragmented; the lower patch is too far right.
Collar relief/grain is coarse and contains pigment imprints. Bowl reflection,
finial glints, crown-tip/rim transitions, socket brightness and base texture
are still imperfect. Side material remains an interpretation with directional
marks. Next separate collar geometric normals from pigment/relief effects;
do not repeat the rejected light-only fit or raise scores on fitting loss alone.
The mission remains active and incomplete.
