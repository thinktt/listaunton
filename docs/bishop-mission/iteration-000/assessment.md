# Initial bishop examination — 2026-11-05

The mission starts from the accepted continuous-head/button model (SHA-256
`3db345fb65a1d9579344456a717f7960f0a3894dc3a95b209cb0fe1ad52f6a3f`).
Its material is diagnostic gray clay. No wood work is present, so wood scores
start at zero rather than inheriting another piece's assessments.

| Category | Initial score |
| --- | ---: |
| Outside silhouette and placement (selected-reference IoU) | 94.88% |
| Interior geometry and carving (visual judgment) | 78% |
| Wood color (visual judgment) | 0% |
| Grain and surface texture (visual judgment) | 0% |
| Lighting and reflections (visual judgment) | 30% |

Equal-weight working mean: **40.58%**. Holistic full-material resemblance:
approximately **30–40%**. These are progress indicators, not recovered-truth
probabilities. Original-white silhouette IoU is **96.58%**; original-black
secondary IoU is **95.96%**, both at the existing fixed registration.

The button is slightly narrower and lower than the selected detail image.
Its broad direct contact and the continuous curved head are valuable accepted
features. The slit is genuinely deep, but its visible width, mouth termination
and reflected edge differ. Collar spacing and socket diameter need close
comparison once the finish is readable. The foot is rounder and the lower
base contour narrower in places than the reference. The gray material has
none of the honey-gold color, growth markings, flecks, fine grain or varnish
variation. Its broad soft highlights do not match the glints on the button,
slit edge, collar crescents, socket and lower-right base.

The selected original image, opposite-color original, full comparison and
head/stem/base crops were inspected. The side guide was inspected separately;
it remains interpretation, not the target camera. The existing model's raw
normalized height is about 80.15% of king before the owner-approved gallery
sliders; the displayed 75.3% is a presentation target. This material iteration
preserves all geometry and gallery defaults rather than applying slider values
to the mesh.

The new mask script uses the mission's largest-component/hole-fill convention.
An initial implementation missed a Pillow writable copy and returned an
obviously invalid 20.7% for every reference; it was corrected before this
baseline was recorded. The regenerated masks and contour images were checked.
Historical scores used raw masks and therefore differ slightly.

Next: preserve geometry/camera, establish actual boxwood pigment and a physical
reflection rig. Use the queen lessons about diffuse/specular separation and
reopened texture validation. No quota monitoring is part of this mission run.
