# Pawn checkpoint 007

Checkpoint 006 (`c22b56a`) leaves a soft, bright join beneath the ball.
The selected reference has a thin dark occlusion line. Both original sprites
support its position.

## Locating the join

Ray intersections separate the actual foreground ball from the shallow
collar behind it. The selected image's steepest brightness drop falls 2.5
output pixels beyond the old geometric edge. A small 0.020-unit adjustment
to the lower cheek brings that drop within half a pixel of the new edge. The
top of the ball, its seated contact and the overall dimensions are retained.
The darkest part of the original black sprite falls 0.5 output pixels beyond
the new edge. The white sprite places its softer minimum 1.5 pixels inside.

## Lighting the collar

Separate light passes identify the left softbox and right bounce as the
principal sources washing out the inner collar. Trial 032 raises the fill
and makes the contact darker, but the shadow extends too far over the wood.
Visibility rays from the collar show why a smaller source can help. At a
60–61° elevation in front of the piece, the ball blocks light close to the
edge. The collar can see the same source four pixels farther out. These are
light angles. The camera remains fixed at 54°.

Trials 033 and 034 fit compact diffuse sources around those directions and
confine the collar reflectors. An attempted reflection behind the ball was
fully occluded and received zero energy. Trial 035 remeasures the diffuse
pigment with the actual full-color, black and neutral renders. The cast
shadow comes from the mesh and light arrangement. Existing pigment carries
through locations where a diffuse estimate is unreliable.

Across the front arc, the selected shadow core measures 4.19 on a 255-level
brightness scale. Trial 031 gave 32.01, trial 032 gave 13.98 and the accepted
render gives 6.33. Six pixels farther out the accepted collar measures 28.69,
against 29.09 in the reference. A thin glint still catches the lower head.
The left base reflection, right-hand lower arc and socket retain visible
differences in shape, peak brightness and surface breakup.

## Reading both references

The widest rear flare just below the collar appears earlier in the originals.
At output row 646 the black and white sprites each span 320 pixels. The
selected enlargement spans 290 and the model spans 315. At row 612 the
widths are 226, 232, 170 and 223 respectively. The original and selected
silhouette masks themselves overlap by 97.01%. The original takes priority
for this shape. See `original-flare.png` and `reference-contours.json`.

The native-size comparison still places all three head-glint centers within
one original pixel. The darker side of the piece is necessarily inferred.
The orbit sheet inspects four azimuths in the studio and again under neutral
fill. The maps turn with the wood; broad bands on the rear look different
from the finer grain visible in the selected view.

## Reproduction

```sh
blender -b --python-exit-code 1 --python scripts/pawn/apply_wood.py -- docs/pawn-mission/iteration-007/reproduction.json
```

The archive supplies checkpoint 006. The recipe reapplies the lower meridian,
diffuse panels, confined reflectors and packed pigment. The scorecard contains
all six trials and the checkpoint record compares the accepted, reopened and
independently replayed renders.

The verified export remains a single closed body with 57,984 triangles.
The maximum fixed-camera error is below 0.000011 pixels in the DOM/WebGL
harness. Model, source-image and candidate page checks pass. The saved and
independent renders differ from the selected trial by at most one RGB level
with identical alpha. The separate shared-set knight metadata discrepancy
was last measured in checkpoint 005.
