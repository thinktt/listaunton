# Bishop iteration 013 — regional wood color and continuity research

The local socket, stem and collar pigment grade is accepted for this
checkpoint. It keeps the accepted geometry, grain layout, relief, light rig and
orthographic 54-degree camera. Foot, lower-base, head and button atlas pixels
remain exact. The saved/reopened render, independent scene audit and existing
anatomy checks pass. The final synchronization checks are recorded in checkpoint.json.

The owner has not requested a pause. The mission remains active and incomplete.
No quota monitoring, other-piece edits or publishing are part of this work.

## What the continuity studies established

The conspicuous side/rear patch cannot be repaired merely by changing roughness
or filling unseen pixels. A separate position/normal bake was projected into an
independently rendered position field. Under the recorded conservative visibility
test, about 88.65% of the old pigment transition is on visible surfaces. This is
an approximate visibility measurement with explicit depth and facing tolerances,
not proof of recovered historical geometry or intrinsic color.

Trial 100 replaces broad color with a robust boxwood tone and bounded fine grain.
It makes the fixed view flat and yellow. Removing broad shading also removes
useful wood variation, while fine residuals still contain false tonal boundaries.
Trial 102 fits 28 measured diffuse-light responses, retaining glossy lighting.
Its actual saved render improves the flat-color control but remains well behind
the accepted version. The same-mask reduced-image error agrees reasonably with
the response prediction; a lower fitting number does not establish fidelity.

Trial 103 removes projected pigment from relief while retaining its former pore
height coefficient. The back becomes more continuous, but the front remains
plastic-looking; fixed-view RGB error barely changes. Trial 104 instead protects
the measured visible atlas and continues broad color harmonically into hidden
surfaces. The front stays close, but the obvious side patch remains. None of
these four candidates replaces checkpoint 012.

The first diffuse-scope check incorrectly assumed new Blender lights had nodes
disabled. Blender 5.2 supplies a neutral emission tree by default. The corrected
audit checks that exact neutral tree, powers, colors, directions, ray visibility
and environment wiring. It then passes without altering the candidate. Initial
failed logs are retained alongside the successful independent audit.

## The smaller useful change

The accepted image is slightly too dark and brown through the middle. Trial 105
applies smooth height-dependent RGB gains to the real wood atlas. It improves
socket, stem and collars, but worsens the foot and does not improve the base.
Trial 106 retains only the middle-body part of that grade. Its height field is
the same around every azimuth, with smooth transitions and no new projected
photograph. The original grain pattern and relief inputs remain in place.

The final comparison uses a fresh render after saving and reopening, with
512 fixed samples. See rgb-statistics.json for the exact regional values and
comparison/stem-socket.png for original, selected reference, previous and current
views. The independent PNG check proves that alpha and protected height bands
remain byte-identical. The scene audit permits only the declared packed atlas
replacement; it preserves meshes, modifiers, UVs, other material nodes/pixels,
lights, render regions, camera, world and render paths.

Foreground RGB error falls from 7.6908 to 7.1865 /255. Socket error decreases
8.1710 → 5.7880, stem 3.2056 → 2.2533 and collars 6.7178 → 6.0016. Foot and button
render differences are negligible. These are diagnostics, not fidelity scores.
Exported positions, normals, indices, bounds and camera are exact. Reevaluating
the Boolean changes 766 evaluated UV components by at most one float32 ULP
(5.96e-8), within the existing 1e-7 bound; control UVs remain exact.

## Five-category assessment

| Category | Previous | Current | Evidence and remaining mismatch |
| --- | ---: | ---: | --- |
| Silhouette/placement | 96.11 | 96.11 | Measured overlap; unchanged geometry and registration. |
| Interior form | 84 | 84 | Continuous head/button and deep slit remain; exact hidden form is inferred. |
| Wood color | 84 | 85 | Middle-body darkness is reduced; broad tone still differs at base and upper head. |
| Grain/surface | 77 | 77 | Markings are retained. Fine relief remains too uniform and the side/rear patch is obvious. |
| Lighting/reflections | 77 | 77 | Lamps unchanged. Socket band is thin/speckled, collar crescents and base/button glints still differ. |

Only silhouette is measured. The other scores are visual judgments. The working
mean is approximately 83.82%, with a holistic fixed-view range of 75–85%.
Every full trial has its own scorecard in studies/ and trials.json. A small color
gain does not resolve the much larger side-material defect or complete the mission.

## Preservation and next work

Checkpoint 012 is archived. Earlier receiver and geometry audits remain strict:
the old receiver/light audit runs on the archived source, followed by a separate
all-state comparison allowing only this atlas. Current slit/contact/anatomy and
export checks also run on the actual saved model. No outline masks, thresholds,
registration or reference pixels are changed.

The pigment is inferred under estimated illumination and retains residual broad
shading; it is not a mathematically recovered, fully de-lit albedo. In particular,
do not repeat a hidden-only fill or constant-tone/global-sun fit and expect the
side patch to disappear without affecting the fixed view. A useful future
continuity study needs joint regional illumination and pigment constraints.
The next local finishing target is the collar reflection shape and its missing
irregular surface detail, while preserving this color result. Side/rear texture,
slit-edge finish and base/button highlights remain explicit unfinished work.
