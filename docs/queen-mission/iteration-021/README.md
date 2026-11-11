# Queen checkpoint 21 — lower the exposed egg

The accepted edit lowers only the exposed finial cap. Control rings 108–116
retain their radii; their heights contract 10% toward ring 107. The actual
mesh becomes 0.038026 units shorter (0.855%).
Every body, bowl, crown-tip and rim control is identical to checkpoint 20.
The cap sits more comfortably inside the crown in profile, and its upper
contour is closer in the fixed reference view. The relative cap/tip gap falls
by about a quarter at the control profile. The imagined side guide supports
this choice but is not treated as recovered geometry.

Only the three existing finial-only glossy reflectors are re-aimed, using
surface positions and actual bump normals at the same measured reference glints.
Their colors, powers (within float precision), radii, links and shadow behavior
are preserved. The other 82 lights are identical. No texture, UV, material node,
camera, body dimension or gallery default changes. The camera remains **54°**.
The height validator accounts explicitly for this additional cap correction
and retains its prior tolerance; the body is not stretched to hide the change.
The displayed 83.4% queen-to-king gallery preset remains a presentation guide.

Original and selected-high-res outline IoUs remain **97.9191%**
and **97.9683%**. Within the finial crop, blurred RGB error
improves **6.03%** against the original; the high-res error
changes **+0.81%**. This is a documented small tradeoff, not a
claim that every pixel improves. The high-res contact-area error improves,
while the original contact-area error rises slightly. Grain direction and
the contact crescent still differ, so material and lighting scores stay fixed.

Scores: silhouette 97.9683 measured; form **86**, color **84**,
grain **79**, lighting **76** estimated. Working mean **84.5937%**;
holistic **80–85%**. The reconstruction remains incomplete.

The larger inner-bowl change is rejected. It helps rays clear the rim, but
its contact shape and bright patch disagree with the original. Adding two
shadowed spot reflectors makes the upscale crescent brighter, while worsening
the original contact fit. Those emitters and that raised bowl are absent from
the accepted model. A more deeply lowered cap config was prepared but not
rendered because the modest lowering already matched the upper contour; it
is not counted as a tested candidate. All five rendered trials are rated in
`scores.json`. The original remains decisive when references conflict.

The rejected bowl trial required preserving light-face membership across a
height threshold. The optional atlas-face mapping in `render_regions.py` and
`refine_socket_flare.py` keeps the exact previous UV membership; missing or
ambiguous matches fail. This option is **off** for the accepted cap. Its
receivers use the existing partition, with exact face, UV and normal checks.

Reproduce the accepted change from the checkpoint-20 archive:

```sh
blender -b --python scripts/queen/profile_study.py -- docs/queen-mission/iteration-021/profile.json --render --samples 256
python scripts/queen/measure_finial_glints.py --out build/queen-mission/finial-targets-021
blender -b --python scripts/queen/capture_collar_surface.py -- --source build/queen-mission/193-lower-egg-cap/queen.blend --out finial-surface-193 --crop 410 135 558 292
blender -b --python scripts/queen/aim_finial_reflections.py -- --source build/queen-mission/193-lower-egg-cap/queen.blend --capture finial-surface-193 --targets finial-targets-021 --variant 195-lower-cap-reaimed --emitter-radius-factor 1 --cone 12
blender -b --python scripts/queen/render_saved_trial.py -- 195-lower-cap-reaimed
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/195-lower-cap-reaimed/queen.blend --report-dir build/queen-mission/195-lower-cap-reaimed
blender -b --python scripts/queen/check_material_geometry.py -- --baseline history/queen-mission-020/queen-rebuilt.blend --current build/queen-mission/195-lower-cap-reaimed/queen.blend --allow-finial-cap --report-dir build/queen-mission/195-lower-cap-reaimed
blender -b --python scripts/queen/validate_cap_lights.py -- build/queen-mission/195-lower-cap-reaimed/queen.blend --out build/queen-mission/195-lower-cap-reaimed
```

Actual 256-sample saved/reopened and published renders agree within the
recorded pixel tolerance. Diagnostic position/normal emission passes are never
used as beauty renders. Mesh, material, light scope, camera, receiver, source,
viewer and tab checks pass. UI checks use a simulated DOM/WebGL harness, not
native browser inspection. Interactive lighting remains approximate.
Fixed and side images and the embedded viewer share model `6ac2fe2309b0e6046db892be11ffbb986059228341c3b7ea140956e792de8c48`.

Remaining problems include the thin contact crescent, broken rear-bowl glints,
base-highlight breakup, some grain directions and the socket's upright wall.
Next isolate contact illumination on the unchanged accepted bowl, rather than
repeating the raised-seat geometry that worsened the source match.
