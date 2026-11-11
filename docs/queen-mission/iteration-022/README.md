# Queen checkpoint 22 — reduce baked shading at the egg root

The accepted change corrects pigment, with checkpoint 21 geometry, camera,
relief and all 85 lights preserved. The pigment-only diagnostic contains a
dark root band even without illumination: median linear luminance is 0.00557
there, compared with 0.02477 on the egg and 0.02587 on the adjacent bowl.
This suggests residual recess shading in the inferred pigment. It is not a
measurement of the unknown original wood albedo.

The correction multiplies existing linear pigment by 1–2.5 inside a smooth
object-space mask. Height rises from 4.025 to 4.065 and falls from 4.08 to
4.14; radial falloff is 0.215–0.245. It retains the grain and hue, the packed
v9 atlas pixels and the independent relief field. The first broader mask
created an orange bowl band and was rejected. The narrower mask affects the
inner root. It works around the actual 3D piece, including when translated,
and is carried into the viewer using the same position-based formula.
The WebGL scene still uses approximate lighting. This is a procedural color
grade, not a newly baked atlas; future exports must retain or bake it explicitly.

Original finial-crop RGB error falls **17.71%**
and contact error **38.14%**. The selected
high-res errors fall **1.99%** and
**4.94%**, respectively. Both bowl-region
errors also improve. These are local blurred RGB diagnostics, not whole-model
fidelity percentages. Outside outline IoUs remain 97.9191%
against the original and 97.9683% against the high-res.

Scores: silhouette 97.9683 measured; form **86**, color **85**,
grain **79**, lighting **76** estimated. The color estimate rises one point;
the other estimates stay fixed. Working mean **84.7937%**, holistic
**80–85%**. The camera remains 54°, height 4.407266 and base diameter 2.072867.
The source images, registration and gallery defaults are unchanged.

Six actual trials are recorded in `scores.json`. Shadowed lights on the
accepted geometry had almost no measured transport: the rim blocks all seven
central rays at the intended contact curve. Tiny sampled-image differences
are not evidence that those ineffective lights help. Raising the bowl floor
cleared the rays, but both the larger and smaller profile edits worsened the
reference match. Fitting new lights to the larger profile did not recover it.
None of those shape changes or extra emitters is in the accepted model.
The opposite-color original was also inspected for the shape of the root.

Reproduce the accepted material edit from the frozen checkpoint-21 archive:

```sh
blender -b --python scripts/queen/grade_finial_root.py -- docs/queen-mission/iteration-022/204-inner-root-pigment.json
blender -b --python scripts/queen/render_saved_trial.py -- 204-inner-root-pigment
blender -b --python scripts/queen/capture_collar_surface.py -- --source history/queen-mission-021/queen-rebuilt.blend --out finial-contact-surface-021 --crop 400 225 570 300
blender -b --python scripts/queen/validate_root_pigment.py -- build/queen-mission/204-inner-root-pigment/queen.blend --out build/queen-mission/204-inner-root-pigment
blender -b --python scripts/queen/check_material_geometry.py -- --baseline history/queen-mission-021/queen-rebuilt.blend --current build/queen-mission/204-inner-root-pigment/queen.blend --report-dir build/queen-mission/204-inner-root-pigment
```

`inspect_surface_components.py` accepts an explicit source hash, preserving
its historical default. Its pigment and reflection passes are diagnostics,
never delivered as beauty images. The rejection configs, target preparation,
actual light responses and fit records preserve the investigation. Intermediate
Blender files may serialize differently when rebuilt: verify geometry and
material scope before substituting a newly generated hash in an experiment.

The saved/reopened and published 256-sample renders agree within one RGB byte.
Geometry, UVs, material scope, lights and camera checks pass. The actual Blender
grade field matches the viewer formula within the recorded sampling tolerance
and follows a translated piece. Fixed/side renders and the viewer share
model `f390b7d335ff020b47ec9eab661e21d69254db7c074832e89c3cf5b735cb27e4`. Numerical browser checks cover camera, material uniforms,
tabs and source integrity; native browser verification is recorded separately.

The thin bright contact crescent itself remains unfinished. Rear-bowl glints,
some coarse grain, base-highlight breakup and the socket wall also differ.
Continue with the accepted pigment correction and investigate the remaining
reflection/relief relationship; do not repeat the rejected raised-floor shapes
or treat the 98% outline measurement as a finished reconstruction.


Final delivery verification: both repository site checks passed. The localhost
response contains the accepted embedded model hash and byte-identical current
fixed and side images. Native browser inspection confirmed the Wood viewer,
Side preset and return to the overlay camera, with no console error messages.
See `delivery-check.json`, `native-browser-check.json` and `site-checks.json`.
The browser lighting remains approximate; this verifies delivery and rendering,
not a new visual-fidelity score.
