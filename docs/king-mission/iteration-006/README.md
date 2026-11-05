# King checkpoint 006 — continuous inferred wood

The accepted change completes the turned body's hidden wood using an evenly lit
generated pigment source. It replaces horizontal smearing and softens the abrupt
orange-to-dark transition when the king is rotated. It retains the central
front detail and the entire cross atlas. The fixed-view pigment is not byte
identical: a broader blend changes grazing surfaces at the sides of collars,
stem, socket and base. The maximum-change crop is included, not hidden in an average.

Geometry, all original UVs/attributes, live lights, relief, dimensions and the
54-degree orthographic camera are unchanged. The closed viewer mesh is byte
identical to checkpoint 005. Four exact render receivers retain their routes.
Temporary completion UVs and mask attributes are removed from the final model.
The result remains an actual Principled BSDF with live reflections.

## Examination and decisions

Trials 076 and 077 were rejected: folding existing pigment onto the back copied
residual glints and left the large side transition. Emission-only diagnostic
views confirmed pigment contributed to the defect. Trial 078 used generated
unlit wood and substantially improved the rear. Trial 079 broadened the blend
on grazing surfaces, softening the side-base boundary. Trial 080 is the accepted
128-sample render of that material, with the temporary data cleaned up. Drafts
used 64 samples; their tiny alpha/IoU differences are sampling, not new geometry.
See scores.json for all five ratings and the decision for each candidate.

The fixed view, enlarged head/collars/socket/base crops, both overlays, neutral,
profile, side and rear renders were inspected. The known clay illumination
cutoff remains. The largest fixed-view change is on the right collar edges,
which become warmer and more detailed. The overall central pattern remains
close to checkpoint 005. The original sprite is still the authority; the high-res
selection and original bytes are unchanged. This pass does not establish a
second-color finish or recover the actual grain on unseen wood.

| Metric | Checkpoint 005 | Checkpoint 006 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.820% | 97.820% |
| Interior form | 83% | 83% |
| Wood color | 82% | 82% |
| Grain and surface texture | 78% | 79% |
| Lighting and reflections | 60% | 60% |
| Equal-weight working mean | 80.164% | 80.364% |

Original IoU is unchanged at 96.833%. Only silhouette is measured; other ratings
are subjective. The small grain improvement credits clearer, continuous texture
at oblique angles, not a claim that invented hidden grain is historically exact.
Holistic assessment remains 73–82%. Mean foreground RGB change from 005 is
1.387/255; the largest channel change is 81/255 at a right collar edge.

## Reproduction

Start from the exact archived history/king-mission-005/king-rebuilt.blend.
Run Blender in background mode with --python-exit-code 1, using:

    scripts/king/complete_hidden_pigment.py -- docs/king-mission/iteration-006/reproduction-config.json

This writes a separate build/king-mission/checkpoint-006-reproduction result.
080-config.json records the accepted asset destination. Both use the unchanged
generated source in assets/king/materials/inferred-wood-source-01.png. Source and
output hashes, the full prompt, and built-in image_gen provenance are recorded in
[hidden-wood-generation.json](hidden-wood-generation.json). The image is a new
material inference made using the selected king as a style reference; it is not
an additional historical reference and does not replace either original image.

The completion script bakes pigment only, restores exact retained texels, packs
the PNG, verifies its saved/reopened pixels, and regenerates the light receivers.
The atlas is assets/king/materials/king-pigment-atlas-v6.png. Blender saves the
actual 54-degree camera before rendering inspection elevations.

## Validation and review

The saved/reopened and fully rebuilt renders have identical alpha and differ
by at most 1/255. The reproduced atlas pixels are identical. Exact editable
geometry, original UVs and attributes (including local varnish relief), material
finish graph, lights/routes, world, camera and color-management checks pass.
Both closed components have positive volume and no nonmanifold edges. Exact
derived receiver regeneration and viewer corner roundtrip pass.

The king review opens Reconstruction and retains Reference overlay, Rotate
model and Side comparison. The same model, atlas and camera are embedded in its
viewer. Repository and local-preview DOM/WebGL harnesses, site/model consistency,
candidate controls, whole-set defaults and historical projection preservation
all pass. All 34 king preview files are hash-verified. Results are recorded in
checkpoint.json, checks/ and preview-sync.json. Native browser inspection was
unavailable because the app-access request timed out; no native screenshot
verification is claimed. DOM/WebGL harness checks are reported separately.

## Remaining work and pause

Foot and base reflections, upper glints, cross seating, collar curvature and
cavity contrast still need work. A warmer side-base patch and some shading
remain in retained pigment. The cross sides/rear and projected relief are not
finished. Browser shading is approximate. This is an accepted improvement, not
a perfect match. The owner requested a pause after this checkpoint; finish its
validation, synchronization and commit, then stop. A future resumed iteration
should inspect the foot using isolated-light responses, preserving this material.
