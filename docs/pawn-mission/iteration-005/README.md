# Pawn checkpoint 005

The previous pawn (`30580a6`) has the correct three head reflections and
good regional pigment. The glints are dull and the reference has more fine
variation within them. This pass holds the camera, geometry and pigment fixed.

Trial 023 measures three full Cycles renders with base and coat roughness
scaled together by 0.55, 1 and 1.85. The resulting UV map varies finish
only where those real responses can explain the observed difference.
Elsewhere, slight variation follows unlit wood pigment. Approximately 2.6%
of the atlas differs from its neutral finish by more than 10%. The dark foot
cut retains its previous stain. Both the Blender material and orbit viewer
read the measured roughness atlas.

Trial 024 reduces the broad head-reflector powers and adds three compact
area emitters. Separate scene-linear responses determine each light power
from the target brightness distribution. Actual fixed render values at the
99th percentile of the left, upper and lower-right glints are 226, 238 and
233 on a 255-level scale. Checkpoint 004 gave 218, 201 and 170. The selected
image gives 244, 248 and 239.

The detail within the glints is still too smooth. Fine brightness contrast
in the upper and right patches rises from 8.5 and 6.5 to 10.6 and 12.0. The
reference measures 18.4 and 20.0. The left patch slips from 13.7 to 9.1,
against 18.3. Its flat white core is visibly different. The next pass will
test bounded surface-normal variation within the wood finish. The lower
flare also needs narrower and more continuous reflections.

## Reproduction

```sh
blender -b --python-exit-code 1 --python scripts/pawn/fit_glint_cores.py -- docs/pawn-mission/iteration-005/reproduction.json
```

The reproduction starts from archived checkpoint 004. The original sprites
and selected image keep the same hashes and registration. The same exported
mesh and UVs carry both pigment and finish. The orbit viewer uses approximate
lighting. The fixed and side views on the page are actual Cycles renders.

The saved and independently replayed renders match the trial to one RGB
level with identical alpha. The viewer checks both embedded map hashes,
the fixed camera, side registration and the controls in the DOM/WebGL
harness. Site links, all model pages and candidate checks pass. The shared
set-height check still reports the separate knight metadata issue recorded
in checkpoint 003.
