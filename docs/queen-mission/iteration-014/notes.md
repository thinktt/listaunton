# Fourteenth queen iteration: socket crescent

Accepted 2026-11-05. Starting checkpoint: 3a1f28b, model
358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6.
Accepted trial 138-socket-pigment-atlas. Delivered model: eac23f7c9bbead43a22ea621f2a05a0604eeeebcc13a131e53ffabaca6302223.
Reference: bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a.

## Examination and changes

The reference socket has two narrow, connected crescent segments with a dimmer
center. The model instead had a large white patch to the right and a stray
glint on the stem. Turning off the three socket-named lights barely changed
the problem. Individual full-BSDF response renders identified the main causes:
base-key, upper-right, collars-right, foot-right, finial-right and lower-right
reflectors spilled onto the stem/socket from other intended targets.

Trial 134 creates a third exact render receiver, stem-socket, between z=.83
and 2.78. The closed editable mesh is unchanged. Six measured stray reflectors
are excluded only from that region; their action elsewhere is retained. The
three old socket lights are disabled. Diffuse illumination remains in place.
Ten overlapping physical spot emitters follow the reference crescent (135).
Native 512-sample full-wood responses fit their powers through AgX (136).
This removes the wrong patches and creates the proper curved highlight.

Removing the old glints reveals two false dark pigment marks. Trial 137 fills
only 2,260 pixels in two bounded ellipses from adjacent log wood color, with
bounded fine and medium grain. Trial 138 bakes this into the v8 UV atlas.
All other pigment, relief, roughness, geometry, UVs and camera are retained.
This is inferred pigment on a real BSDF, not a substituted reference image.
The fixed render and actual side render were inspected after saving/reopening.

## Scores and evidence

Before: outline 97.9612 measured, form 82, color 83, grain 79, lighting 67;
working mean 81.7922%, holistic 77-82%.
After: outline 97.9612 measured, form 82, color 84, grain 79, lighting 70;
working mean 82.5922%, holistic 78-83%.
Original IoU remains 97.9109%.
Only IoU is measured fidelity; the other scores are subjective visual estimates.
The actual-render socket-region error decreases 10.9%. This local
statistic supports the visual comparison but is not whole-model accuracy.

| Trial | Outline | Form | Color | Grain | Lighting | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| 134 | 97.96 | 82 | 83 | 79 | 65 | reject alone |
| 135 | 97.96 | 82 | 83 | 79 | 69 | superseded |
| 136 | 97.96 | 82 | 83 | 79 | 70 | superseded |
| 137 | 97.96 | 82 | 84 | 79 | 70 | superseded by portable atlas |
| 138 | 97.96 | 82 | 84 | 79 | 70 | accept |

Lighting gains three points for the correctly placed crescent and removal of
stray patches; color gains one for repairing the exposed pigment marks. Form
and grain scores are unchanged: the geometry is identical and broader grain
pattern/relief discrepancies remain. The side view has less of the former
vertical reflected stripe on the stem, consistent with removing those lights.
No new surface join is visible in the inspected views.

## Verification and reproduction

Control coordinates, topology and atlas UVs match checkpoint 13 exactly.
The three derived receivers collectively preserve every evaluated face, UV,
smooth corner normal and material from that closed surface. The validator
also checks the stem/socket bounds, control hash and exact light links.
The model remains closed and manifold at 54 degrees with the same finial and
height/base ratio. Source images and side-gallery defaults are untouched.

Reproduce from tracked inputs:

```sh
blender -b --python scripts/queen/rebuild_socket_checkpoint.py -- docs/queen-mission/iteration-014/reproduction.json
```

This produces private trial 139-reproduced-socket-checkpoint from the archived
checkpoint 13, v8 atlas and recorded light rig. Saved/reopened and reproduction
pixel results are recorded in accepted-material-reproduction-check.json.
The archive remains in history/queen-mission-013. Diagnostic builders and fitting
scripts are preserved in scripts/queen; pass the archived source explicitly
when repeating a historical diagnostic. Rebuild receivers after geometry edits
using socket_band=True for this checkpoint. Do not restore a two-region receiver
over the new lighting configuration. UI checks use the established DOM/WebGL
harness; no native browser GPU inspection is claimed.

## Remaining discrepancies and next action

The socket crescent is still somewhat sharper and narrower than the reference,
with the small underlying orange/dark grain variations not perfectly reproduced.
The bowl/finial reflections and collar highlights remain fragmented, the front
rim lacks its precise flattened faces, and the wood's broad grain and fine pores
still differ. The base highlight remains too broad in its lower half and the
foot's dark groove/bright edge need further work. Browser lighting is approximate.

Next isolate the collar reflections: reproduce the narrow rolled edges and
connected crescents while preserving the now improved socket and base.
The mission remains active and incomplete.
