# Thirteenth queen iteration: base junction, pigment and reflection

Accepted on 2026-11-05. Start: checkpoint 12, commit 0531df7,
model SHA-256 2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b.
Accepted trial: 132-grained-base-atlas. Delivered model SHA-256: 358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6.
Reference SHA-256: bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a.

## Examination and decisions

The base glint was too pale, low and wide, with a dark notch and a thin bright
ridge below the socket. Changing relief alone (120) made the reflection more
rippled. Moving, narrowing and warming the physical base reflector (121-122)
improved its appearance but did not remove the notch. Isolated light responses
identified collar, foot and socket reflectors spilling onto the base; narrowing
those three lights (123-124) did not justify the extra rig complexity.

Neutral renders showed a small geometric ledge. Trial 125 replaces only the
radii of rings 26-29 with a Hermite transition from the flare to the socket.
Maximum displacement is 0.017977953 units. Every height and every other control
vertex remains identical; UVs and topology remain identical. The exact evaluated
body and finial receivers are regenerated from the edited closed control.

A pigment-only diagnostic revealed a second cause: the v5 color field contains
a dark highlight-shaped imprint. Removing normal inputs did not remove it.
Trials 126-129 reconstruct this local pigment from adjacent wood in log color,
with bounded fine reference grain. The fixed view improved, but side inspection
caught an overly plain orange patch, so 129 was rejected despite passing its
technical checks. Trial 130 adds bounded medium grain from the existing relief
field. 131 combines that repair with 125 geometry and only the 122 base light.
132 bakes the pigment into the portable v7 atlas without changing relief,
roughness, other lights or geometry. The original references remain unchanged.

The active bump is strength 0.45, distance 0.007, with scale-140 pores. Older
stored config fields do not describe those actual shader inputs. The v7 atlas
contains pigment only, with real BSDF lighting; no photograph replaces a render.
The medium grain is an artistic inference, not recovered original wood data.

## Scores

Only silhouette is measured; all other scores are subjective, approximate
visual judgments. The working mean is not a probability of correctness.
Before: 97.9612 / 81 / 82 / 79 / 65, mean 80.9922%, holistic 76-81%.
After: 97.9612 / 82 / 83 / 79 / 67, mean 81.7922%, holistic 77-82%.
Original silhouette IoU stays 97.9109%; selected-reference IoU stays 97.9612%.
The 64-sample accepted alpha is exactly unchanged. Small earlier-trial IoU
differences reflect sampling/antialiasing, not deliberate outline changes.

| Trial | Outline | Form | Color | Grain | Lighting | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| 120 | 97.96 | 81 | 82 | 77 | 64 | reject |
| 121 | 97.96 | 81 | 82 | 79 | 65 | superseded |
| 122 | 97.96 | 81 | 83 | 79 | 66 | light component accepted in combined candidate |
| 123 | 97.96 | 81 | 83 | 79 | 65 | not promoted |
| 124 | 97.96 | 81 | 83 | 79 | 66 | not promoted |
| 125 | 97.96 | 82 | 82 | 79 | 65 | component accepted |
| 126 | 97.96 | 81 | 83 | 78 | 65 | superseded |
| 127 | 97.96 | 82 | 83 | 78 | 65 | superseded |
| 128 | 97.96 | 82 | 83 | 78 | 67 | superseded |
| 129 | 97.96 | 82 | 83 | 78 | 67 | reject |
| 130 | 97.96 | 82 | 83 | 79 | 65 | component accepted |
| 131 | 97.96 | 82 | 83 | 79 | 67 | superseded by portable atlas |
| 132 | 97.96 | 82 | 83 | 79 | 67 | accept |

Form gains one point for the smoother base/socket junction. Color gains one
for removing the false dark imprint and warmer base appearance. Lighting gains
two for the warmer, narrower reflection without the ledge. Grain stays 79:
the local patch is repaired but the larger pattern and relief remain imperfect.

## Verification and reproduction

The final model retains the fixed 54-degree orthographic camera, adjusted
height/base tolerance and deeper finial. Mesh closure, topology, four-ring
scope, identical UVs and exact receiver faces/normals/material/links pass.
Saved/reopened and independently rebuilt renders differ by at most one RGB
byte, with identical alpha. See material-reproduction-check and delivered
validation reports. Side inspection is an actual Cycles render. UI checks
use the established DOM/WebGL harness, not a native GPU browser inspection.

Rebuild the accepted model from the tracked checkpoint-12 archive, four ring
radii, v7 pigment texture and recorded base light:

```sh
blender -b --python scripts/queen/rebuild_base_checkpoint.py -- docs/queen-mission/iteration-013/reproduction.json
```

Output is private trial 133-reproduced-base-checkpoint, not the public model.
The existing scripts also preserve the experiments: smooth_base_transition,
inspect_base_material, prepare_base_pigment_repair, apply_base_pigment_repair,
reshape_base_reflector, fit_base_reflector_color, combine_base_refinement and
bake_pigment_atlas. Use the archived baseline explicitly when re-running them.
Their accepted parameters and diagnostic evidence are stored beside this file.
V6 was rejected and removed from public assets; its private trial remains.

## Remaining discrepancies

- Bowl and finial glints are still too separate and too pale; the reference's
  curved rear glint and small front crescent are not reproduced precisely.
- Crown-tip shoulders and flat rim intervals still have softer shading/form.
- Collar reflections are fragmented; the socket needs a continuous narrow
  crescent instead of the current white patch and separate marks.
- The repaired base reflection is still too broad/low in its lower portion;
  the reference has a taller textured streak and different fine pore relief.
- Broad wood pattern, fine pores and gloss still differ. The side view is
  usable but retains projection-derived pattern and reflection limitations.
- Foot groove depth and its bright edge still read differently from reference.

Next: isolate the socket's white patch from its missing continuous crescent,
checking neutral curvature and individual reflectors before editing either.
The queen mission remains active and incomplete.
