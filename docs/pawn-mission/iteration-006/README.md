# Pawn checkpoint 006

The previous finish (`da74174`) placed the three glints correctly, but wide
patches of smooth white light obscured the walnut. The reference's fine
ridges remain visible through the highlights.

Trial 026 measures five full renders. One uses the existing wood normals.
The others tilt the same finish by small positive and negative slopes in
each UV tangent direction. A bounded fit recovers surface directions where
these measured responses explain the local contrast. Hidden faces carry
small slopes from the unlit wood. The median added tilt is 0.63°, the 99th
percentile is 2.43° and the maximum is 4.86°. This treatment changes how
light reflects from a real surface as the viewer moves.

The two crops in `base-reflection-study.png` subtract the same real render
with the base reflectors disabled from the reference and from the model.
The reference residual includes pigment and shape differences. It shows a
narrow second arc across the front right of the flare. On the left, the highlight extends beyond the
previous patch. Trial 027 fits shorter area sources along these arcs using
native 1,254-pixel Cycles light responses. It recovers more of the right
arc but leaves some pale, blocky reflections.

Trial 028 measures seven emitter groups separately and fits the red, green
and blue output of each group. It compares local chromaticity, displayed
brightness percentiles and pixel error. The bright upper and right glints
now sit in warmer walnut, and the socket and flare pick up warmer light.
The left flare still ends too abruptly. Its bright end and the thin wood
grain across it need more contrast. The lower head meets the collar with a
softer shadow than in either reference.

## Original sprite and side

`native-comparison.png` shows the untouched black sprite next to the
selected enlargement and both model versions, sampled at the sprite's
original resolution using the saved registration. The three glint centers
differ from the original by 0.90, 0.73 and 0.75 native pixels. The selected
enlargement itself differs by 0.74, 0.52 and 0.97 pixels. The original is
softer and darker overall. Across common foreground, original-to-model mean
RGB error is 17.37/255, down from 17.42/255. The selected enlargement gives
15.74/255. The side render checks that the finish stays on the turned piece.

## Reproduction

```sh
blender -b --python-exit-code 1 --python scripts/pawn/tune_light_color.py -- docs/pawn-mission/iteration-006/reproduction.json
```

The configuration starts from archived checkpoint 005, attaches the static
slope atlas, rebuilds the flare reflectors and restores their measured
spectra. The browser uses the same pigment, varnish and slope atlases with
approximate lighting.

The geometry and UV export is byte-identical to checkpoint 005. Reopened
and independently replayed renders have identical alpha and differ from
the trial by at most one RGB level. The synchronized viewer passes its
DOM/WebGL camera, interaction and three-map checks. All model pages,
original hashes and candidate controls pass. The separate historical knight
height metadata issue was last checked at checkpoint 005.
