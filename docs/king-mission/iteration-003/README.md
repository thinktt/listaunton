# King checkpoint 003: curved cross cap

The cross now has a shallow arched cap edge and a gently rounded upper contour.
Its bevel strips use smooth normals. The physical height, base diameter, complete
turned body and fixed 54-degree camera are preserved. This is a refinement of
checkpoint 002, not a new model. The original and selected reference images are
unchanged; the original's clipped cross still represents missing evidence.

The first lowered-cap trial was rejected. Pixel crops showed its actual edge
below the reference, with a second edge retained in the old pigment. The final
curve preserves center height and lowers only the ends. Separate real glossy
lights illuminate the cross; body glossy lights are linked to the turned body.
Five cross light powers were fitted from actual linear Cycles responses, then
judged in the full BSDF render. Light separation is an artistic reconstruction,
not a claim that the original studio rig has been recovered.

A bounded cross-only diffuse-pigment estimate corrects markings displaced by
the curve change. The body material is excluded. Before the final bake, old
atlas UVs are retained for sampling and new cross islands are unwrapped.
The body atlas columns are copied exactly from v3, avoiding a second filtering
pass. V4 remains pigment under a real Principled material and live lighting.
Residual source shading and unseen-surface interpretation remain limitations.

## Assessment

| Metric | Previous | Current |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.849% | 97.826% |
| Interior form | 80% | 82% |
| Wood color | 80% | 81% |
| Grain and surface texture | 76% | 77% |
| Lighting and reflections | 54% | 55% |
| Equal-weight mean | 77.570% | 78.565% |

Original-sprite IoU rises from 96.795% to 96.824%. The small high-res silhouette
tradeoff comes with a closer cap curve and slightly better original agreement;
it does not establish that the cross is exact. Only IoU is measured. The other
values are subjective visual ratings; holistic assessment remains 70–80%.
The side guide remains an imagining, and the white finish is not scored here.

The cross reflections are still too thin and regular. Its lower seating and
negative space differ, collar edges are too shelf-like, cavity contrast is weak,
and base reflections are overly central and broad. The foot and socket remain
too rounded in places. Side inspection still shows an abrupt orange-to-dark
transition into inferred horizontal grain. These are unresolved defects.

## Validation and reproduction

The mesh has two closed, positive-volume components and 70,364 triangles. The
body controls, topology, transform, subdivision, evaluated positions and atlas
UVs are exactly preserved. Height and base diameter are unchanged. The camera
is exactly preserved at 54.0000008 degrees. The export reproduces every evaluated
triangle corner, normal and UV, and the viewer camera regression is below
0.000050 pixels. Packed PNG bytes match the external atlas; packed pixels and
the retained body atlas region survive saving and reopening exactly.

The reopened beauty render differs by at most 1/255 in a channel, with a mean
of 0.00000652/255. Final bake versus pre-atlas mean foreground RGB difference is
0.0259/255. Unchanged body geometry/pigment does not imply bit-identical rendered
body pixels: altered cross reflections and indirect illumination also matter.
The mean change below the crown is 0.6233/255 relative to checkpoint 002.

Run Blender with `--background --python-exit-code 1 --python
scripts/king/rebuild_checkpoint_003.py -- FRESH_LABEL` to reconstruct the chain
from `history/king-mission-002/king-rebuilt.blend`. Outputs stay under build and
do not replace accepted files. Inputs are 024 through 028 config files here.
For only the final atlas bake, run `scripts/king/bake_pigment.py` with
`reproduction.json`, using the packed source in `history/king-mission-003-pre-atlas`.
`check_cross_checkpoint.py` verifies the intentional geometry scope; the older
material-only geometry check correctly does not apply to a changed cross.

The complete reconstruction chain was executed from archived checkpoint 002.
Its final render has identical alpha and a mean foreground error of
0.000147/255. Two adjacent cross-glint pixels differ by more than 1/255, with
a maximum of 4/255; independent fitted powers vary slightly and 303 cross-atlas
pixels quantize differently by 1/255. The body atlas remains identical. These
localized differences were inspected after the initial stricter comparison
flagged them; see `full-reproduction-check.json` and `reproduction-differences.json`.

The king main review opens Reconstruction, with synchronized Reference overlay,
Rotate model and Side comparison. Candidate choices and historical projections
remain available. The page, mesh, renders, model and material are copied to the
existing local preview. Interaction validation uses the actual page in a
simulated DOM/WebGL harness; native screenshot validation is not claimed.
Site, source, candidate, whole-set defaults and historical projection checks pass.

Next: investigate the oversized base reflection using isolated light responses
and the actual base curvature. Keep the new cross, accepted body proportions and
54-degree registration while testing. Broader, grain-broken cross glints and a
continuous hidden finish remain separate follow-up targets. The mission is active
and incomplete.
