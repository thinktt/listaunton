# Pawn checkpoint 003

The starting model is checkpoint 002 (`834a82e`). Black pawn candidate 2
supplies detail. The original black and white sprites take priority where
the contours differ. Every full render uses the same 54° orthographic camera.

## Shape

The previous upper flare was too wide behind the stem. A bounded fit of eight
lathe rings to the two sprite silhouettes reduced the predicted half-width
error in that region from 5.47 to 1.24 output pixels. The actual render
confirms the change. A second pass flattens the bottom fillet and deepens the
single undercut. The clay and side views still show one turned groove.

## Finish and light

Isolated Cycles light passes identified the socket reflector responsible for
the vertical streak on the stem and a foot reflector spilling into the cut.
The retained rig keeps the three head highlights and fits narrower lower
reflectors against the selected image. Black and gray response renders measure
the diffuse wood again on the revised geometry. The continuous UV atlas carries
the inferred visible grain and the existing unlit walnut onto the hidden faces.

At fixed pixel (484, 952), the selected groove is RGB (6, 2, 2).
Reregistering the wood gave (49, 23, 10). A darker, less polished finish
following the recess around the actual turning gives (6, 1, 0). At row 958
the final RGB is (49, 26, 16) against (51, 25, 16). This finish is a material
interpretation. The precise original wood treatment is unknown.

The lower highlights remain broad patches. The reference has thinner,
broken arcs and finer varnish texture. The lower head still looks longer
and merges with the collar more softly than in the original and the elevated
candidate. These are the next shape and finish priorities.

## Reproduction

The archive holds the editable checkpoint 002 scene. The reproduction applies
the measured ring edits, rebuilds the fitted lower reflectors, attaches the
packed pigment and applies the local groove-polish curve.

```sh
blender -b --python-exit-code 1 --python scripts/pawn/apply_wood.py -- docs/pawn-mission/iteration-003/reproduction.json
```

`scorecard.json` records all five trials. `checkpoint.json` contains the
delivered and replayed render comparisons. The review uses this same mesh,
camera and pigment for its fixed, side and interactive views.

The site links, all model sources and candidate tab tests pass. The pawn's
interactive DOM/WebGL check verifies the packed pigment and the 54° camera.
The full-set check passes the image and candidate comparisons, then stops
on the knight's historical height metadata. It expects knight mesh metadata
starting `104c1917` and finds `2ff3631c` after separate knight work. The
pawn's archived height source still matches its recorded hash.
