# King checkpoint 002: measured pigment and crown reflections

The geometry and orthographic 54-degree camera are preserved. Two real glossy
spot reflectors target the crown platter and cross bevel, with separate body
and cross receivers. A diffuse pigment estimate uses black/white renders of
the actual Principled material to approximate the local light response.
AgX is inverted once; the byte-backed PNG is already encoded sRGB. The supplied
cutout has small alpha variations within the piece, so confidence is continuous.
Glints, dark shadows, low illumination and strong specular mismatch keep the
previous pigment. Fine reference grain also drives shallow varnish relief.

This recovers the broad base figure and more of the stem/collar color variation.
The atlas contains pigment; actual BSDF shading, reflections and shadows remain
live. Inversion is approximate: residual source shading can remain in pigment,
and single-view evidence does not uniquely determine albedo or hidden surfaces.

Current scores: silhouette 97.8494%, interior form 80%, wood color 80%, grain and
surface texture 76%, lighting 54%; equal-weight mean 77.5699%. Original-sprite IoU
is 96.7945%. Holistic estimate: 70â€“80%. Only IoU is a measured percentage.

Remaining issues include straight cross bevel glints where the reference has
curved edges, inaccurate cross seating, shelf-like collars, weak cavity contrast,
overly broad/central base reflections, some orange pigment transitions and a
visible change to inferred horizontal grain on the hidden half. The latter is
more apparent after improving the front; it remains a priority, not a claim of
a finished all-angle material. White-piece finish is not assessed by these scores.
The original black sprite retains priority and its clipped cross is missing
evidence. Geometry and accepted gallery sizing are unchanged.

The mirrored hidden-grain trial, front-face cross reflector, and first pigment
input conversion were rejected. Weak varnish relief was not promoted. The final
atlas bake initially caught an input/prepared-file hash mix-up; the corrected
pipeline validates the input source separately from its prepared render scene.

Editable vertex positions, face topology, transforms, subdivision settings and
camera are identical to checkpoint 001. Evaluated subdivision differs only by
floating-point roundoff after added UV layers: position <=4.77e-7 model units,
normal component <=2.19e-5, UV <=1.79e-7. The two components remain closed and
positive-volume, with 68,492 triangles. Packed PNG bytes match the external atlas,
and packed pixels survive reopening exactly. Reopened beauty differs by at most
1/255 in a channel, with mean 0.00000811/255. Atlas versus pre-bake mean foreground
RGB difference is 0.1884/255. Viewer checks cover the real page in a simulated
DOM/WebGL harness; native browser screenshot validation is not claimed.

## Reproduction

Run Blender with `--background --python-exit-code 1 --python
scripts/king/rebuild_checkpoint_002.py -- FRESH_LABEL` from a context where the
script path resolves. It starts from `history/king-mission-001/king-rebuilt.blend`,
rebuilds reflectors, captures black/white response, infers pigment, adds coat
relief and bakes the final atlas. All outputs remain under
`build/king-mission/FRESH_LABEL`; accepted files are not overwritten.

For just the final bake, use `scripts/king/bake_pigment.py` with
`docs/king-mission/iteration-002/reproduction.json`. The packed pre-atlas source
is preserved in `history/king-mission-002-pre-atlas`. The original references
and generated pigment source remain unchanged.

After accepting future work, export with `export_mission.py`, validate the saved
scene, rebuild the side comparison and viewer, and refresh only the king review
page. Synchronize the local Windows preview and commit the checked iteration.
The next hypothesis is to round the cross cap/bevel geometry while preserving
the accepted pigment, outline, 54-degree camera and physical height/base ratio;
then isolate the oversized base reflection. Keep hidden-finish continuity on the
remaining-issues list rather than masking it with a reference-view score.

The full rebuild was executed from checkpoint 001 in a fresh build directory.
It reproduced the accepted beauty with identical alpha, maximum 1/255 channel
difference and mean foreground RGB difference 0.0000715/255. The historical king
projection check and set controls also passed. Thirty king preview files were
copied and verified by hash. See full-reproduction-check.json and preview-sync.json.
